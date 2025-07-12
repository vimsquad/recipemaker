"""Tests for the Recipe Maker database."""

import pytest
import tempfile
import json
import os
from datetime import datetime

from recipemaker.database import RecipeDatabase
from recipemaker.models import RecipeCreate, RecipeUpdate


class TestRecipeDatabase:
    """Test RecipeDatabase class."""
    
    @pytest.fixture
    def temp_db_file(self):
        """Create a temporary database file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            yield f.name
        os.unlink(f.name)
    
    @pytest.fixture
    def db(self, temp_db_file):
        """Create a fresh database instance."""
        return RecipeDatabase(temp_db_file)
    
    @pytest.fixture
    def sample_recipe_data(self):
        """Sample recipe data for testing."""
        return RecipeCreate(
            title="Test Recipe",
            description="A test recipe",
            ingredients=["ingredient 1", "ingredient 2"],
            instructions=["step 1", "step 2"],
            prep_time=15,
            cook_time=30,
            servings=4,
            difficulty="Easy",
            cuisine="Italian"
        )
    
    def test_create_recipe(self, db, sample_recipe_data):
        """Test creating a recipe."""
        recipe = db.create_recipe(sample_recipe_data)
        assert recipe.id == 1
        assert recipe.title == "Test Recipe"
        assert recipe.ingredients == ["ingredient 1", "ingredient 2"]
        assert recipe.instructions == ["step 1", "step 2"]
        assert recipe.prep_time == 15
        assert recipe.cook_time == 30
        assert recipe.servings == 4
        assert recipe.difficulty == "Easy"
        assert recipe.cuisine == "Italian"
        assert recipe.created_at is not None
        assert recipe.updated_at is not None
    
    def test_get_recipe(self, db, sample_recipe_data):
        """Test getting a recipe by ID."""
        created_recipe = db.create_recipe(sample_recipe_data)
        retrieved_recipe = db.get_recipe(created_recipe.id)
        assert retrieved_recipe is not None
        assert retrieved_recipe.title == "Test Recipe"
    
    def test_get_nonexistent_recipe(self, db):
        """Test getting a recipe that doesn't exist."""
        recipe = db.get_recipe(999)
        assert recipe is None
    
    def test_get_all_recipes(self, db, sample_recipe_data):
        """Test getting all recipes."""
        recipe1 = db.create_recipe(sample_recipe_data)
        recipe2_data = RecipeCreate(
            title="Another Recipe",
            ingredients=["ingredient 3"],
            instructions=["step 3"]
        )
        recipe2 = db.create_recipe(recipe2_data)
        
        all_recipes = db.get_all_recipes()
        assert len(all_recipes) == 2
        assert all_recipes[0].id == 1
        assert all_recipes[1].id == 2
    
    def test_update_recipe(self, db, sample_recipe_data):
        """Test updating a recipe."""
        recipe = db.create_recipe(sample_recipe_data)
        update_data = RecipeUpdate(title="Updated Recipe", difficulty="Medium")
        updated_recipe = db.update_recipe(recipe.id, update_data)
        
        assert updated_recipe.title == "Updated Recipe"
        assert updated_recipe.difficulty == "Medium"
        assert updated_recipe.ingredients == ["ingredient 1", "ingredient 2"]  # unchanged
        # The updated_at should be different or equal (in case of very fast execution)
        assert updated_recipe.updated_at >= recipe.updated_at
    
    def test_update_nonexistent_recipe(self, db):
        """Test updating a recipe that doesn't exist."""
        update_data = RecipeUpdate(title="Updated Recipe")
        result = db.update_recipe(999, update_data)
        assert result is None
    
    def test_delete_recipe(self, db, sample_recipe_data):
        """Test deleting a recipe."""
        recipe = db.create_recipe(sample_recipe_data)
        assert len(db.get_all_recipes()) == 1
        
        success = db.delete_recipe(recipe.id)
        assert success is True
        assert len(db.get_all_recipes()) == 0
    
    def test_delete_nonexistent_recipe(self, db):
        """Test deleting a recipe that doesn't exist."""
        success = db.delete_recipe(999)
        assert success is False
    
    def test_search_recipes_by_query(self, db, sample_recipe_data):
        """Test searching recipes by query."""
        db.create_recipe(sample_recipe_data)
        recipe2_data = RecipeCreate(
            title="Chicken Pasta",
            ingredients=["chicken", "pasta"],
            instructions=["cook chicken", "boil pasta"]
        )
        db.create_recipe(recipe2_data)
        
        # Search by title
        results = db.search_recipes(query="chicken")
        assert len(results) == 1
        assert results[0].title == "Chicken Pasta"
        
        # Search by ingredient
        results = db.search_recipes(query="ingredient 1")
        assert len(results) == 1
        assert results[0].title == "Test Recipe"
    
    def test_search_recipes_by_cuisine(self, db, sample_recipe_data):
        """Test searching recipes by cuisine."""
        db.create_recipe(sample_recipe_data)
        recipe2_data = RecipeCreate(
            title="Mexican Recipe",
            ingredients=["tortilla"],
            instructions=["heat tortilla"],
            cuisine="Mexican"
        )
        db.create_recipe(recipe2_data)
        
        results = db.search_recipes(cuisine="Mexican")
        assert len(results) == 1
        assert results[0].title == "Mexican Recipe"
    
    def test_search_recipes_by_difficulty(self, db, sample_recipe_data):
        """Test searching recipes by difficulty."""
        db.create_recipe(sample_recipe_data)
        recipe2_data = RecipeCreate(
            title="Hard Recipe",
            ingredients=["complex ingredient"],
            instructions=["complex step"],
            difficulty="Hard"
        )
        db.create_recipe(recipe2_data)
        
        results = db.search_recipes(difficulty="Hard")
        assert len(results) == 1
        assert results[0].title == "Hard Recipe"
    
    def test_search_recipes_by_max_time(self, db, sample_recipe_data):
        """Test searching recipes by maximum time."""
        db.create_recipe(sample_recipe_data)  # 45 minutes total
        recipe2_data = RecipeCreate(
            title="Quick Recipe",
            ingredients=["quick ingredient"],
            instructions=["quick step"],
            prep_time=5,
            cook_time=10
        )
        db.create_recipe(recipe2_data)  # 15 minutes total
        
        results = db.search_recipes(max_time=20)
        assert len(results) == 1
        assert results[0].title == "Quick Recipe"
    
    def test_persistence(self, temp_db_file, sample_recipe_data):
        """Test that data persists between database instances."""
        # Create first database instance and add recipe
        db1 = RecipeDatabase(temp_db_file)
        recipe = db1.create_recipe(sample_recipe_data)
        
        # Create second database instance and verify data
        db2 = RecipeDatabase(temp_db_file)
        retrieved_recipe = db2.get_recipe(recipe.id)
        assert retrieved_recipe is not None
        assert retrieved_recipe.title == "Test Recipe"
    
    def test_corrupted_file_handling(self, temp_db_file):
        """Test handling of corrupted JSON file."""
        # Write invalid JSON to file
        with open(temp_db_file, 'w') as f:
            f.write("invalid json content")
        
        # Database should handle corruption gracefully
        db = RecipeDatabase(temp_db_file)
        assert len(db.get_all_recipes()) == 0
        assert db.next_id == 1