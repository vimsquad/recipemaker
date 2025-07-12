"""Tests for the Recipe Maker CLI."""

import pytest
from click.testing import CliRunner
import tempfile
import json
import os

from recipemaker.cli import main
from recipemaker.database import RecipeDatabase


@pytest.fixture
def temp_db_file():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def runner(temp_db_file):
    """Create a CLI runner with a temporary database."""
    # Override the global database with a temporary one
    from recipemaker.database import db
    original_db = db
    db.__class__ = RecipeDatabase
    db.__init__(temp_db_file)
    
    runner = CliRunner()
    yield runner
    
    # Restore original database
    db.__class__ = original_db.__class__
    db.__dict__.update(original_db.__dict__)


class TestCLICommands:
    """Test CLI commands."""
    
    def test_add_recipe(self, runner):
        """Test adding a recipe via CLI."""
        result = runner.invoke(main, [
            'add',
            '--title', 'Test Recipe',
            '--description', 'A test recipe',
            '--ingredients', 'ingredient 1,ingredient 2',
            '--instructions', 'step 1,step 2',
            '--prep-time', '15',
            '--cook-time', '30',
            '--servings', '4',
            '--difficulty', 'Easy',
            '--cuisine', 'Italian'
        ])
        
        assert result.exit_code == 0
        assert "Recipe 'Test Recipe' created with ID 1" in result.output
    
    def test_add_recipe_missing_required_fields(self, runner):
        """Test adding a recipe with missing required fields."""
        result = runner.invoke(main, [
            'add',
            '--title', 'Test Recipe'
        ])
        
        assert result.exit_code != 0
        assert "Missing option" in result.output
    
    def test_list_recipes_empty(self, runner):
        """Test listing recipes when none exist."""
        result = runner.invoke(main, ['list'])
        
        assert result.exit_code == 0
        assert "No recipes found" in result.output
    
    def test_list_recipes_with_data(self, runner):
        """Test listing recipes with data."""
        # Add a recipe first
        runner.invoke(main, [
            'add',
            '--title', 'Test Recipe',
            '--ingredients', 'ingredient 1',
            '--instructions', 'step 1'
        ])
        
        result = runner.invoke(main, ['list'])
        
        assert result.exit_code == 0
        assert "Test Recipe" in result.output
        assert "1. Test Recipe" in result.output
    
    def test_show_recipe(self, runner):
        """Test showing a specific recipe."""
        # Add a recipe first
        runner.invoke(main, [
            'add',
            '--title', 'Test Recipe',
            '--description', 'A test recipe',
            '--ingredients', 'ingredient 1,ingredient 2',
            '--instructions', 'step 1,step 2',
            '--prep-time', '15',
            '--cook-time', '30',
            '--servings', '4',
            '--difficulty', 'Easy',
            '--cuisine', 'Italian'
        ])
        
        result = runner.invoke(main, ['show', '1'])
        
        assert result.exit_code == 0
        assert "=== Test Recipe ===" in result.output
        assert "Description: A test recipe" in result.output
        assert "1. ingredient 1" in result.output
        assert "2. ingredient 2" in result.output
        assert "1. step 1" in result.output
        assert "2. step 2" in result.output
        assert "Prep: 15 minutes" in result.output
        assert "Cook: 30 minutes" in result.output
        assert "Servings: 4" in result.output
        assert "Difficulty: Easy" in result.output
        assert "Cuisine: Italian" in result.output
    
    def test_show_nonexistent_recipe(self, runner):
        """Test showing a recipe that doesn't exist."""
        result = runner.invoke(main, ['show', '999'])
        
        assert result.exit_code == 0
        assert "Recipe with ID 999 not found" in result.output
    
    def test_update_recipe(self, runner):
        """Test updating a recipe."""
        # Add a recipe first
        runner.invoke(main, [
            'add',
            '--title', 'Test Recipe',
            '--ingredients', 'ingredient 1',
            '--instructions', 'step 1'
        ])
        
        # Update the recipe
        result = runner.invoke(main, [
            'update', '1',
            '--title', 'Updated Recipe',
            '--difficulty', 'Medium'
        ])
        
        assert result.exit_code == 0
        assert "Recipe 'Updated Recipe' updated successfully" in result.output
        
        # Verify the update
        show_result = runner.invoke(main, ['show', '1'])
        assert "=== Updated Recipe ===" in show_result.output
        assert "Difficulty: Medium" in show_result.output
    
    def test_update_nonexistent_recipe(self, runner):
        """Test updating a recipe that doesn't exist."""
        result = runner.invoke(main, [
            'update', '999',
            '--title', 'Updated Recipe'
        ])
        
        assert result.exit_code == 0
        assert "Recipe with ID 999 not found" in result.output
    
    def test_update_recipe_no_data(self, runner):
        """Test updating a recipe with no data."""
        result = runner.invoke(main, ['update', '1'])
        
        assert result.exit_code == 0
        assert "No update data provided" in result.output
    
    def test_delete_recipe(self, runner):
        """Test deleting a recipe."""
        # Add a recipe first
        runner.invoke(main, [
            'add',
            '--title', 'Test Recipe',
            '--ingredients', 'ingredient 1',
            '--instructions', 'step 1'
        ])
        
        # Delete the recipe
        result = runner.invoke(main, ['delete', '1'])
        
        assert result.exit_code == 0
        assert "Recipe with ID 1 deleted successfully" in result.output
        
        # Verify it's deleted
        list_result = runner.invoke(main, ['list'])
        assert "No recipes found" in list_result.output
    
    def test_delete_nonexistent_recipe(self, runner):
        """Test deleting a recipe that doesn't exist."""
        result = runner.invoke(main, ['delete', '999'])
        
        assert result.exit_code == 0
        assert "Recipe with ID 999 not found" in result.output
    
    def test_search_recipes_by_query(self, runner):
        """Test searching recipes by query."""
        # Add recipes
        runner.invoke(main, [
            'add',
            '--title', 'Test Recipe',
            '--ingredients', 'ingredient 1',
            '--instructions', 'step 1'
        ])
        runner.invoke(main, [
            'add',
            '--title', 'Chicken Pasta',
            '--ingredients', 'chicken,pasta',
            '--instructions', 'cook chicken,boil pasta'
        ])
        
        # Search by title
        result = runner.invoke(main, ['search', '--query', 'chicken'])
        
        assert result.exit_code == 0
        assert "Found 1 recipe(s)" in result.output
        assert "Chicken Pasta" in result.output
    
    def test_search_recipes_by_cuisine(self, runner):
        """Test searching recipes by cuisine."""
        # Add recipes
        runner.invoke(main, [
            'add',
            '--title', 'Test Recipe',
            '--ingredients', 'ingredient 1',
            '--instructions', 'step 1'
        ])
        runner.invoke(main, [
            'add',
            '--title', 'Mexican Recipe',
            '--ingredients', 'tortilla',
            '--instructions', 'heat tortilla',
            '--cuisine', 'Mexican'
        ])
        
        # Search by cuisine
        result = runner.invoke(main, ['search', '--cuisine', 'Mexican'])
        
        assert result.exit_code == 0
        assert "Found 1 recipe(s)" in result.output
        assert "Mexican Recipe" in result.output
    
    def test_search_recipes_by_difficulty(self, runner):
        """Test searching recipes by difficulty."""
        # Add recipes
        runner.invoke(main, [
            'add',
            '--title', 'Test Recipe',
            '--ingredients', 'ingredient 1',
            '--instructions', 'step 1'
        ])
        runner.invoke(main, [
            'add',
            '--title', 'Hard Recipe',
            '--ingredients', 'complex ingredient',
            '--instructions', 'complex step',
            '--difficulty', 'Hard'
        ])
        
        # Search by difficulty
        result = runner.invoke(main, ['search', '--difficulty', 'Hard'])
        
        assert result.exit_code == 0
        assert "Found 1 recipe(s)" in result.output
        assert "Hard Recipe" in result.output
    
    def test_search_recipes_by_max_time(self, runner):
        """Test searching recipes by maximum time."""
        # Add recipes
        runner.invoke(main, [
            'add',
            '--title', 'Test Recipe',
            '--ingredients', 'ingredient 1',
            '--instructions', 'step 1',
            '--prep-time', '15',
            '--cook-time', '30'
        ])
        runner.invoke(main, [
            'add',
            '--title', 'Quick Recipe',
            '--ingredients', 'quick ingredient',
            '--instructions', 'quick step',
            '--prep-time', '5',
            '--cook-time', '10'
        ])
        
        # Search by max time
        result = runner.invoke(main, ['search', '--max-time', '20'])
        
        assert result.exit_code == 0
        assert "Found 1 recipe(s)" in result.output
        assert "Quick Recipe" in result.output
    
    def test_search_recipes_no_results(self, runner):
        """Test searching recipes with no results."""
        result = runner.invoke(main, ['search', '--query', 'nonexistent'])
        
        assert result.exit_code == 0
        assert "No recipes found matching the criteria" in result.output
    
    def test_help(self, runner):
        """Test help command."""
        result = runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert "Recipe Maker" in result.output
        assert "add" in result.output
        assert "list" in result.output
        assert "show" in result.output
        assert "update" in result.output
        assert "delete" in result.output
        assert "search" in result.output