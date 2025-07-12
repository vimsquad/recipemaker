"""Tests for the Recipe Maker models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from recipemaker.models import RecipeBase, RecipeCreate, RecipeUpdate, Recipe, RecipeList, SearchQuery


class TestRecipeBase:
    """Test RecipeBase model."""
    
    def test_valid_recipe_base(self):
        """Test creating a valid RecipeBase."""
        data = {
            "title": "Test Recipe",
            "description": "A test recipe",
            "ingredients": ["ingredient 1", "ingredient 2"],
            "instructions": ["step 1", "step 2"],
            "prep_time": 15,
            "cook_time": 30,
            "servings": 4,
            "difficulty": "Easy",
            "cuisine": "Italian"
        }
        recipe = RecipeBase(**data)
        assert recipe.title == "Test Recipe"
        assert recipe.ingredients == ["ingredient 1", "ingredient 2"]
        assert recipe.instructions == ["step 1", "step 2"]
    
    def test_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            RecipeBase(title="Test")
        
        with pytest.raises(ValidationError):
            RecipeBase(ingredients=["ingredient 1"])
    
    def test_empty_ingredients(self):
        """Test that empty ingredients list raises ValidationError."""
        with pytest.raises(ValidationError):
            RecipeBase(
                title="Test Recipe",
                ingredients=[],
                instructions=["step 1"]
            )
    
    def test_empty_instructions(self):
        """Test that empty instructions list raises ValidationError."""
        with pytest.raises(ValidationError):
            RecipeBase(
                title="Test Recipe",
                ingredients=["ingredient 1"],
                instructions=[]
            )
    
    def test_title_length_validation(self):
        """Test title length validation."""
        # Too short
        with pytest.raises(ValidationError):
            RecipeBase(
                title="",
                ingredients=["ingredient 1"],
                instructions=["step 1"]
            )
        
        # Too long
        with pytest.raises(ValidationError):
            RecipeBase(
                title="a" * 201,
                ingredients=["ingredient 1"],
                instructions=["step 1"]
            )


class TestRecipeCreate:
    """Test RecipeCreate model."""
    
    def test_recipe_create_inheritance(self):
        """Test that RecipeCreate inherits from RecipeBase."""
        data = {
            "title": "Test Recipe",
            "ingredients": ["ingredient 1"],
            "instructions": ["step 1"]
        }
        recipe = RecipeCreate(**data)
        assert isinstance(recipe, RecipeBase)
        assert recipe.title == "Test Recipe"


class TestRecipeUpdate:
    """Test RecipeUpdate model."""
    
    def test_recipe_update_optional_fields(self):
        """Test that all fields in RecipeUpdate are optional."""
        recipe = RecipeUpdate()
        assert recipe.title is None
        assert recipe.ingredients is None
        assert recipe.instructions is None
    
    def test_recipe_update_partial_data(self):
        """Test updating with partial data."""
        data = {"title": "Updated Title"}
        recipe = RecipeUpdate(**data)
        assert recipe.title == "Updated Title"
        assert recipe.description is None


class TestRecipe:
    """Test Recipe model."""
    
    def test_recipe_with_metadata(self):
        """Test creating a Recipe with metadata."""
        now = datetime.now()
        data = {
            "id": 1,
            "title": "Test Recipe",
            "ingredients": ["ingredient 1"],
            "instructions": ["step 1"],
            "created_at": now,
            "updated_at": now
        }
        recipe = Recipe(**data)
        assert recipe.id == 1
        assert recipe.created_at == now
        assert recipe.updated_at == now


class TestRecipeList:
    """Test RecipeList model."""
    
    def test_recipe_list(self):
        """Test creating a RecipeList."""
        recipes = [
            Recipe(
                id=1,
                title="Recipe 1",
                ingredients=["ingredient 1"],
                instructions=["step 1"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        recipe_list = RecipeList(
            recipes=recipes,
            total=1,
            page=1,
            per_page=10
        )
        assert len(recipe_list.recipes) == 1
        assert recipe_list.total == 1


class TestSearchQuery:
    """Test SearchQuery model."""
    
    def test_search_query_optional_fields(self):
        """Test that all fields in SearchQuery are optional."""
        query = SearchQuery()
        assert query.query is None
        assert query.cuisine is None
        assert query.difficulty is None
        assert query.max_time is None
    
    def test_search_query_with_data(self):
        """Test creating SearchQuery with data."""
        data = {
            "query": "chicken",
            "cuisine": "Italian",
            "difficulty": "Easy",
            "max_time": 60
        }
        query = SearchQuery(**data)
        assert query.query == "chicken"
        assert query.cuisine == "Italian"
        assert query.difficulty == "Easy"
        assert query.max_time == 60
    
    def test_search_query_max_time_validation(self):
        """Test max_time validation."""
        with pytest.raises(ValidationError):
            SearchQuery(max_time=-1)