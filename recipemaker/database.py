"""Simple in-memory database for recipe storage."""

from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from pathlib import Path

from .models import Recipe, RecipeCreate, RecipeUpdate


class RecipeDatabase:
    """In-memory database for storing recipes."""
    
    def __init__(self, storage_file: Optional[str] = None):
        self.storage_file = storage_file
        self.recipes: Dict[int, Recipe] = {}
        self.next_id = 1
        self._load_data()
    
    def _load_data(self) -> None:
        """Load recipes from storage file if it exists."""
        if self.storage_file and Path(self.storage_file).exists():
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.recipes = {
                        int(k): Recipe(**v) for k, v in data.get('recipes', {}).items()
                    }
                    self.next_id = data.get('next_id', 1)
            except (json.JSONDecodeError, KeyError, ValueError):
                # If file is corrupted, start fresh
                self.recipes = {}
                self.next_id = 1
    
    def _save_data(self) -> None:
        """Save recipes to storage file."""
        if self.storage_file:
            data = {
                'recipes': {
                    str(k): v.model_dump() for k, v in self.recipes.items()
                },
                'next_id': self.next_id
            }
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
    
    def create_recipe(self, recipe_data: RecipeCreate) -> Recipe:
        """Create a new recipe."""
        now = datetime.now()
        recipe = Recipe(
            id=self.next_id,
            **recipe_data.model_dump(),
            created_at=now,
            updated_at=now
        )
        self.recipes[self.next_id] = recipe
        self.next_id += 1
        self._save_data()
        return recipe
    
    def get_recipe(self, recipe_id: int) -> Optional[Recipe]:
        """Get a recipe by ID."""
        return self.recipes.get(recipe_id)
    
    def get_all_recipes(self) -> List[Recipe]:
        """Get all recipes."""
        return list(self.recipes.values())
    
    def update_recipe(self, recipe_id: int, recipe_data: RecipeUpdate) -> Optional[Recipe]:
        """Update an existing recipe."""
        if recipe_id not in self.recipes:
            return None
        
        recipe = self.recipes[recipe_id]
        update_data = recipe_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(recipe, field, value)
        
        recipe.updated_at = datetime.now()
        self._save_data()
        return recipe
    
    def delete_recipe(self, recipe_id: int) -> bool:
        """Delete a recipe."""
        if recipe_id in self.recipes:
            del self.recipes[recipe_id]
            self._save_data()
            return True
        return False
    
    def search_recipes(self, query: Optional[str] = None, 
                      cuisine: Optional[str] = None,
                      difficulty: Optional[str] = None,
                      max_time: Optional[int] = None) -> List[Recipe]:
        """Search recipes by various criteria."""
        results = list(self.recipes.values())
        
        if query:
            query_lower = query.lower()
            results = [
                r for r in results
                if (query_lower in r.title.lower() or
                    query_lower in (r.description or "").lower() or
                    any(query_lower in ing.lower() for ing in r.ingredients))
            ]
        
        if cuisine:
            cuisine_lower = cuisine.lower()
            results = [r for r in results if r.cuisine and cuisine_lower in r.cuisine.lower()]
        
        if difficulty:
            results = [r for r in results if r.difficulty == difficulty]
        
        if max_time is not None:
            results = [
                r for r in results
                if (r.prep_time or 0) + (r.cook_time or 0) <= max_time
            ]
        
        return results


# Global database instance
db = RecipeDatabase("recipes.json")