"""Tests for the Recipe Maker API endpoints."""

import pytest
from fastapi.testclient import TestClient
import tempfile
import json
import os

from recipemaker.main import app
from recipemaker.database import RecipeDatabase
from recipemaker.models import RecipeCreate


@pytest.fixture
def temp_db_file():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def client(temp_db_file):
    """Create a test client with a temporary database."""
    # Override the global database with a temporary one for each test
    from recipemaker.database import db
    original_storage = db.storage_file
    db.storage_file = temp_db_file
    db.recipes = {}
    db.next_id = 1
    
    yield TestClient(app)
    
    # Restore original database
    db.storage_file = original_storage
    db.recipes = {}
    db.next_id = 1


@pytest.fixture
def sample_recipe_data():
    """Sample recipe data for testing."""
    return {
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


class TestRecipeEndpoints:
    """Test recipe API endpoints."""
    
    def test_create_recipe(self, client, sample_recipe_data):
        """Test creating a recipe via API."""
        response = client.post("/api/v1/recipes", json=sample_recipe_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == "Test Recipe"
        assert data["ingredients"] == ["ingredient 1", "ingredient 2"]
        assert data["instructions"] == ["step 1", "step 2"]
        assert data["id"] == 1
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_recipe_missing_required_fields(self, client):
        """Test creating a recipe with missing required fields."""
        response = client.post("/api/v1/recipes", json={"title": "Test Recipe"})
        assert response.status_code == 422
    
    def test_get_recipe(self, client, sample_recipe_data):
        """Test getting a recipe via API."""
        # Create a recipe first
        create_response = client.post("/api/v1/recipes", json=sample_recipe_data)
        recipe_id = create_response.json()["id"]
        
        # Get the recipe
        response = client.get(f"/api/v1/recipes/{recipe_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Test Recipe"
        assert data["id"] == recipe_id
    
    def test_get_nonexistent_recipe(self, client):
        """Test getting a recipe that doesn't exist."""
        response = client.get("/api/v1/recipes/999")
        assert response.status_code == 404
    
    def test_list_recipes(self, client, sample_recipe_data):
        """Test listing recipes via API."""
        # Create two recipes
        client.post("/api/v1/recipes", json=sample_recipe_data)
        recipe2_data = {
            "title": "Another Recipe",
            "ingredients": ["ingredient 3"],
            "instructions": ["step 3"]
        }
        client.post("/api/v1/recipes", json=recipe2_data)
        
        # List recipes
        response = client.get("/api/v1/recipes")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Test Recipe"
        assert data[1]["title"] == "Another Recipe"
    
    def test_list_recipes_pagination(self, client, sample_recipe_data):
        """Test recipe list pagination."""
        # Create multiple recipes
        for i in range(5):
            recipe_data = sample_recipe_data.copy()
            recipe_data["title"] = f"Recipe {i+1}"
            client.post("/api/v1/recipes", json=recipe_data)
        
        # Test pagination
        response = client.get("/api/v1/recipes?skip=2&limit=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Recipe 3"
        assert data[1]["title"] == "Recipe 4"
    
    def test_update_recipe(self, client, sample_recipe_data):
        """Test updating a recipe via API."""
        # Create a recipe first
        create_response = client.post("/api/v1/recipes", json=sample_recipe_data)
        recipe_id = create_response.json()["id"]
        
        # Update the recipe
        update_data = {"title": "Updated Recipe", "difficulty": "Medium"}
        response = client.put(f"/api/v1/recipes/{recipe_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Updated Recipe"
        assert data["difficulty"] == "Medium"
        assert data["ingredients"] == ["ingredient 1", "ingredient 2"]  # unchanged
    
    def test_update_nonexistent_recipe(self, client):
        """Test updating a recipe that doesn't exist."""
        response = client.put("/api/v1/recipes/999", json={"title": "Updated"})
        assert response.status_code == 404
    
    def test_delete_recipe(self, client, sample_recipe_data):
        """Test deleting a recipe via API."""
        # Create a recipe first
        create_response = client.post("/api/v1/recipes", json=sample_recipe_data)
        recipe_id = create_response.json()["id"]
        
        # Delete the recipe
        response = client.delete(f"/api/v1/recipes/{recipe_id}")
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/recipes/{recipe_id}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_recipe(self, client):
        """Test deleting a recipe that doesn't exist."""
        response = client.delete("/api/v1/recipes/999")
        assert response.status_code == 404


class TestSearchEndpoints:
    """Test search API endpoints."""
    
    def test_search_recipes_by_query(self, client, sample_recipe_data):
        """Test searching recipes by query."""
        # Create recipes
        client.post("/api/v1/recipes", json=sample_recipe_data)
        recipe2_data = {
            "title": "Chicken Pasta",
            "ingredients": ["chicken", "pasta"],
            "instructions": ["cook chicken", "boil pasta"]
        }
        client.post("/api/v1/recipes", json=recipe2_data)
        
        # Search by title
        response = client.get("/api/v1/recipes/search?query=chicken")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Chicken Pasta"
    
    def test_search_recipes_by_cuisine(self, client, sample_recipe_data):
        """Test searching recipes by cuisine."""
        # Create recipes
        client.post("/api/v1/recipes", json=sample_recipe_data)
        recipe2_data = {
            "title": "Mexican Recipe",
            "ingredients": ["tortilla"],
            "instructions": ["heat tortilla"],
            "cuisine": "Mexican"
        }
        client.post("/api/v1/recipes", json=recipe2_data)
        
        # Search by cuisine
        response = client.get("/api/v1/recipes/search?cuisine=Mexican")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Mexican Recipe"
    
    def test_search_recipes_by_difficulty(self, client, sample_recipe_data):
        """Test searching recipes by difficulty."""
        # Create recipes
        client.post("/api/v1/recipes", json=sample_recipe_data)
        recipe2_data = {
            "title": "Hard Recipe",
            "ingredients": ["complex ingredient"],
            "instructions": ["complex step"],
            "difficulty": "Hard"
        }
        client.post("/api/v1/recipes", json=recipe2_data)
        
        # Search by difficulty
        response = client.get("/api/v1/recipes/search?difficulty=Hard")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Hard Recipe"
    
    def test_search_recipes_by_max_time(self, client, sample_recipe_data):
        """Test searching recipes by maximum time."""
        # Create recipes
        client.post("/api/v1/recipes", json=sample_recipe_data)  # 45 minutes total
        recipe2_data = {
            "title": "Quick Recipe",
            "ingredients": ["quick ingredient"],
            "instructions": ["quick step"],
            "prep_time": 5,
            "cook_time": 10
        }
        client.post("/api/v1/recipes", json=recipe2_data)  # 15 minutes total
        
        # Search by max time
        response = client.get("/api/v1/recipes/search?max_time=20")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Quick Recipe"
    
    def test_search_recipes_multiple_criteria(self, client, sample_recipe_data):
        """Test searching recipes with multiple criteria."""
        # Create recipes
        client.post("/api/v1/recipes", json=sample_recipe_data)
        recipe2_data = {
            "title": "Easy Mexican Recipe",
            "ingredients": ["tortilla"],
            "instructions": ["heat tortilla"],
            "cuisine": "Mexican",
            "difficulty": "Easy"
        }
        client.post("/api/v1/recipes", json=recipe2_data)
        
        # Search with multiple criteria
        response = client.get("/api/v1/recipes/search?cuisine=Mexican&difficulty=Easy")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Easy Mexican Recipe"


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "total_recipes" in data