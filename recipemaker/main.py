"""Main FastAPI application for Recipe Maker."""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path

from .api import router as api_router
from .database import db

# Create FastAPI app
app = FastAPI(
    title="Recipe Maker",
    description="A FastAPI-based recipe management application with web UI",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files
app.mount("/static", StaticFiles(directory="recipemaker/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="recipemaker/templates")

# Include API routes
app.include_router(api_router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with recipe list."""
    recipes = db.get_all_recipes()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "recipes": recipes}
    )


@app.get("/recipe/{recipe_id}", response_class=HTMLResponse)
async def recipe_detail(request: Request, recipe_id: int):
    """Recipe detail page."""
    recipe = db.get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return templates.TemplateResponse(
        "recipe_detail.html",
        {"request": request, "recipe": recipe}
    )


@app.get("/recipe/new", response_class=HTMLResponse)
async def new_recipe_form(request: Request):
    """New recipe form page."""
    return templates.TemplateResponse(
        "recipe_form.html",
        {"request": request, "recipe": None}
    )


@app.get("/recipe/{recipe_id}/edit", response_class=HTMLResponse)
async def edit_recipe_form(request: Request, recipe_id: int):
    """Edit recipe form page."""
    recipe = db.get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return templates.TemplateResponse(
        "recipe_form.html",
        {"request": request, "recipe": recipe}
    )


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """Search page."""
    query = request.query_params.get("q", "")
    cuisine = request.query_params.get("cuisine", "")
    difficulty = request.query_params.get("difficulty", "")
    
    recipes = db.search_recipes(
        query=query if query else None,
        cuisine=cuisine if cuisine else None,
        difficulty=difficulty if difficulty else None
    )
    
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "recipes": recipes,
            "query": query,
            "cuisine": cuisine,
            "difficulty": difficulty
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)