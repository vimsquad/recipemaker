"""Command-line interface for Recipe Maker using Click."""

import click
from typing import List, Optional
import json

from .database import db
from .models import RecipeCreate, RecipeUpdate


@click.group()
def main():
    """Recipe Maker - A command-line interface for managing recipes."""
    pass


@main.command()
@click.option('--title', '-t', required=True, help='Recipe title')
@click.option('--description', '-d', help='Recipe description')
@click.option('--ingredients', '-i', required=True, help='Comma-separated list of ingredients')
@click.option('--instructions', '-s', required=True, help='Comma-separated list of cooking instructions')
@click.option('--prep-time', type=int, help='Preparation time in minutes')
@click.option('--cook-time', type=int, help='Cooking time in minutes')
@click.option('--servings', type=int, help='Number of servings')
@click.option('--difficulty', type=click.Choice(['Easy', 'Medium', 'Hard']), help='Difficulty level')
@click.option('--cuisine', help='Cuisine type')
def add(title: str, description: Optional[str], ingredients: str, instructions: str,
        prep_time: Optional[int], cook_time: Optional[int], servings: Optional[int],
        difficulty: Optional[str], cuisine: Optional[str]):
    """Add a new recipe."""
    recipe_data = RecipeCreate(
        title=title,
        description=description,
        ingredients=[ing.strip() for ing in ingredients.split(',')],
        instructions=[inst.strip() for inst in instructions.split(',')],
        prep_time=prep_time,
        cook_time=cook_time,
        servings=servings,
        difficulty=difficulty,
        cuisine=cuisine
    )
    
    recipe = db.create_recipe(recipe_data)
    click.echo(f"Recipe '{recipe.title}' created with ID {recipe.id}")


@main.command()
def list():
    """List all recipes."""
    recipes = db.get_all_recipes()
    if not recipes:
        click.echo("No recipes found.")
        return
    
    for recipe in recipes:
        click.echo(f"\n{recipe.id}. {recipe.title}")
        if recipe.description:
            click.echo(f"   Description: {recipe.description}")
        click.echo(f"   Difficulty: {recipe.difficulty or 'Not specified'}")
        click.echo(f"   Cuisine: {recipe.cuisine or 'Not specified'}")
        if recipe.prep_time or recipe.cook_time:
            total_time = (recipe.prep_time or 0) + (recipe.cook_time or 0)
            click.echo(f"   Total time: {total_time} minutes")


@main.command()
@click.argument('recipe_id', type=int)
def show(recipe_id: int):
    """Show details of a specific recipe."""
    recipe = db.get_recipe(recipe_id)
    if not recipe:
        click.echo(f"Recipe with ID {recipe_id} not found.")
        return
    
    click.echo(f"\n=== {recipe.title} ===")
    if recipe.description:
        click.echo(f"Description: {recipe.description}")
    
    click.echo(f"\nIngredients:")
    for i, ingredient in enumerate(recipe.ingredients, 1):
        click.echo(f"  {i}. {ingredient}")
    
    click.echo(f"\nInstructions:")
    for i, instruction in enumerate(recipe.instructions, 1):
        click.echo(f"  {i}. {instruction}")
    
    if recipe.prep_time or recipe.cook_time:
        click.echo(f"\nTime:")
        if recipe.prep_time:
            click.echo(f"  Prep: {recipe.prep_time} minutes")
        if recipe.cook_time:
            click.echo(f"  Cook: {recipe.cook_time} minutes")
    
    if recipe.servings:
        click.echo(f"Servings: {recipe.servings}")
    
    if recipe.difficulty:
        click.echo(f"Difficulty: {recipe.difficulty}")
    
    if recipe.cuisine:
        click.echo(f"Cuisine: {recipe.cuisine}")
    
    click.echo(f"\nCreated: {recipe.created_at}")
    click.echo(f"Updated: {recipe.updated_at}")


@main.command()
@click.argument('recipe_id', type=int)
@click.option('--title', '-t', help='New recipe title')
@click.option('--description', '-d', help='New recipe description')
@click.option('--ingredients', '-i', help='Comma-separated list of ingredients')
@click.option('--instructions', '-s', help='Comma-separated list of cooking instructions')
@click.option('--prep-time', type=int, help='Preparation time in minutes')
@click.option('--cook-time', type=int, help='Cooking time in minutes')
@click.option('--servings', type=int, help='Number of servings')
@click.option('--difficulty', type=click.Choice(['Easy', 'Medium', 'Hard']), help='Difficulty level')
@click.option('--cuisine', help='Cuisine type')
def update(recipe_id: int, title: Optional[str], description: Optional[str],
           ingredients: Optional[str], instructions: Optional[str],
           prep_time: Optional[int], cook_time: Optional[int], servings: Optional[int],
           difficulty: Optional[str], cuisine: Optional[str]):
    """Update an existing recipe."""
    update_data = {}
    
    if title:
        update_data['title'] = title
    if description is not None:
        update_data['description'] = description
    if ingredients:
        update_data['ingredients'] = [ing.strip() for ing in ingredients.split(',')]
    if instructions:
        update_data['instructions'] = [inst.strip() for inst in instructions.split(',')]
    if prep_time is not None:
        update_data['prep_time'] = prep_time
    if cook_time is not None:
        update_data['cook_time'] = cook_time
    if servings is not None:
        update_data['servings'] = servings
    if difficulty:
        update_data['difficulty'] = difficulty
    if cuisine:
        update_data['cuisine'] = cuisine
    
    if not update_data:
        click.echo("No update data provided. Use --help to see available options.")
        return
    
    recipe_update = RecipeUpdate(**update_data)
    recipe = db.update_recipe(recipe_id, recipe_update)
    
    if recipe:
        click.echo(f"Recipe '{recipe.title}' updated successfully.")
    else:
        click.echo(f"Recipe with ID {recipe_id} not found.")


@main.command()
@click.argument('recipe_id', type=int)
def delete(recipe_id: int):
    """Delete a recipe."""
    if db.delete_recipe(recipe_id):
        click.echo(f"Recipe with ID {recipe_id} deleted successfully.")
    else:
        click.echo(f"Recipe with ID {recipe_id} not found.")


@main.command()
@click.option('--query', '-q', help='Search term')
@click.option('--cuisine', help='Filter by cuisine')
@click.option('--difficulty', type=click.Choice(['Easy', 'Medium', 'Hard']), help='Filter by difficulty')
@click.option('--max-time', type=int, help='Maximum total time in minutes')
def search(query: Optional[str], cuisine: Optional[str], difficulty: Optional[str], max_time: Optional[int]):
    """Search recipes by various criteria."""
    recipes = db.search_recipes(
        query=query,
        cuisine=cuisine,
        difficulty=difficulty,
        max_time=max_time
    )
    
    if not recipes:
        click.echo("No recipes found matching the criteria.")
        return
    
    click.echo(f"Found {len(recipes)} recipe(s):")
    for recipe in recipes:
        click.echo(f"\n{recipe.id}. {recipe.title}")
        if recipe.description:
            click.echo(f"   Description: {recipe.description}")
        click.echo(f"   Difficulty: {recipe.difficulty or 'Not specified'}")
        click.echo(f"   Cuisine: {recipe.cuisine or 'Not specified'}")


if __name__ == '__main__':
    main()