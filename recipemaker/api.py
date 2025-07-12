"""FastAPI routes for the Recipe Maker application."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from .models import Recipe, RecipeCreate, RecipeUpdate, RecipeList, SearchQuery
from .database import db

router = APIRouter(prefix="/api/v1", tags=["recipes"])


@router.post("/recipes", response_model=Recipe, status_code=201)
async def create_recipe(recipe_data: RecipeCreate) -> Recipe:
    """Create a new recipe."""
    return db.create_recipe(recipe_data)


@router.get("/recipes", response_model=List[Recipe])
async def list_recipes(
    skip: int = Query(0, ge=0, description="Number of recipes to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of recipes to return")
) -> List[Recipe]:
    """Get all recipes with pagination."""
    recipes = db.get_all_recipes()
    return recipes[skip:skip + limit]


@router.get("/recipes/search", response_model=List[Recipe])
async def search_recipes(
    query: Optional[str] = Query(None, description="Search term"),
    cuisine: Optional[str] = Query(None, description="Filter by cuisine"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    max_time: Optional[int] = Query(None, ge=0, description="Maximum total time in minutes")
) -> List[Recipe]:
    """Search recipes by various criteria."""
    return db.search_recipes(
        query=query,
        cuisine=cuisine,
        difficulty=difficulty,
        max_time=max_time
    )


@router.get("/recipes/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: int) -> Recipe:
    """Get a specific recipe by ID."""
    recipe = db.get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.put("/recipes/{recipe_id}", response_model=Recipe)
async def update_recipe(recipe_id: int, recipe_data: RecipeUpdate) -> Recipe:
    """Update an existing recipe."""
    recipe = db.update_recipe(recipe_id, recipe_data)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.delete("/recipes/{recipe_id}", status_code=204)
async def delete_recipe(recipe_id: int) -> None:
    """Delete a recipe."""
    if not db.delete_recipe(recipe_id):
        raise HTTPException(status_code=404, detail="Recipe not found")


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "total_recipes": len(db.get_all_recipes())}