"""Data models for the Recipe Maker application."""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class RecipeBase(BaseModel):
    """Base recipe model with common fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Recipe title")
    description: Optional[str] = Field(None, max_length=500, description="Recipe description")
    ingredients: List[str] = Field(..., min_length=1, description="List of ingredients")
    instructions: List[str] = Field(..., min_length=1, description="Cooking instructions")
    prep_time: Optional[int] = Field(None, ge=0, description="Preparation time in minutes")
    cook_time: Optional[int] = Field(None, ge=0, description="Cooking time in minutes")
    servings: Optional[int] = Field(None, ge=1, description="Number of servings")
    difficulty: Optional[str] = Field(None, description="Difficulty level (Easy, Medium, Hard)")
    cuisine: Optional[str] = Field(None, description="Cuisine type")


class RecipeCreate(RecipeBase):
    """Model for creating a new recipe."""
    pass


class RecipeUpdate(BaseModel):
    """Model for updating an existing recipe."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    ingredients: Optional[List[str]] = Field(None, min_length=1)
    instructions: Optional[List[str]] = Field(None, min_length=1)
    prep_time: Optional[int] = Field(None, ge=0)
    cook_time: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    difficulty: Optional[str] = None
    cuisine: Optional[str] = None


class Recipe(RecipeBase):
    """Complete recipe model with metadata."""
    id: int = Field(..., description="Unique recipe identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class RecipeList(BaseModel):
    """Model for recipe list responses."""
    recipes: List[Recipe]
    total: int
    page: int
    per_page: int


class SearchQuery(BaseModel):
    """Model for recipe search queries."""
    query: Optional[str] = Field(None, description="Search term")
    cuisine: Optional[str] = Field(None, description="Filter by cuisine")
    difficulty: Optional[str] = Field(None, description="Filter by difficulty")
    max_time: Optional[int] = Field(None, ge=0, description="Maximum total time in minutes")