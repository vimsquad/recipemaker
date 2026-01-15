#!/usr/bin/env python3
"""
Recipe Scaler - A Python program to scale recipes from one serving size to another.

This program allows you to input a recipe with ingredients and their quantities,
then scale it to a different number of servings while maintaining proper proportions.
"""

import re
import click
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class Ingredient:
    """Represents a single ingredient with quantity, unit, and name."""
    quantity: Decimal
    unit: str
    name: str
    
    def __str__(self) -> str:
        """Return a formatted string representation of the ingredient."""
        if self.quantity == int(self.quantity):
            quantity_str = str(int(self.quantity))
        else:
            quantity_str = str(self.quantity)
        
        if self.unit:
            return f"{quantity_str} {self.unit} {self.name}"
        else:
            return f"{quantity_str} {self.name}"


@dataclass
class Recipe:
    """Represents a complete recipe with ingredients and serving size."""
    name: str
    original_servings: int
    ingredients: List[Ingredient]
    instructions: Optional[List[str]] = None
    
    def scale_to_servings(self, new_servings: int) -> 'Recipe':
        """Scale the recipe to a new number of servings."""
        if new_servings <= 0:
            raise ValueError("Number of servings must be positive")
        
        scaling_factor = Decimal(new_servings) / Decimal(self.original_servings)
        
        scaled_ingredients = []
        for ingredient in self.ingredients:
            new_quantity = ingredient.quantity * scaling_factor
            # Round to 2 decimal places for better readability
            new_quantity = new_quantity.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            scaled_ingredients.append(Ingredient(
                quantity=new_quantity,
                unit=ingredient.unit,
                name=ingredient.name
            ))
        
        return Recipe(
            name=f"{self.name} (Scaled to {new_servings} servings)",
            original_servings=new_servings,
            ingredients=scaled_ingredients,
            instructions=self.instructions
        )


class RecipeParser:
    """Parser for converting text input into Recipe objects."""
    
    # Common units for recipe ingredients
    UNITS = {
        'cup', 'cups', 'tbsp', 'tbsps', 'tablespoon', 'tablespoons',
        'tsp', 'tsps', 'teaspoon', 'teaspoons', 'oz', 'ounce', 'ounces',
        'lb', 'lbs', 'pound', 'pounds', 'g', 'gram', 'grams',
        'kg', 'kilogram', 'kilograms', 'ml', 'milliliter', 'milliliters',
        'l', 'liter', 'liters', 'fl oz', 'fluid ounce', 'fluid ounces',
        'pinch', 'dash', 'clove', 'cloves', 'bunch', 'bunches',
        'can', 'cans', 'jar', 'jars', 'package', 'packages'
    }
    
    @classmethod
    def parse_ingredient_line(cls, line: str) -> Optional[Ingredient]:
        """Parse a single ingredient line into an Ingredient object."""
        line = line.strip()
        if not line:
            return None
        
        # Pattern to match: quantity unit name
        # Examples: "2 cups flour", "1/2 tsp salt", "3 large eggs"
        pattern = r'^(\d+(?:\.\d+)?(?:\/\d+)?)\s*([a-zA-Z\s]+?)\s+(.+)$'
        match = re.match(pattern, line)
        
        if not match:
            # Try pattern without unit: "3 eggs", "2 tomatoes"
            pattern_no_unit = r'^(\d+(?:\.\d+)?(?:\/\d+)?)\s+(.+)$'
            match = re.match(pattern_no_unit, line)
            if match:
                quantity_str, name = match.groups()
                return cls._create_ingredient(quantity_str, "", name.strip())
            return None
        
        quantity_str, unit, name = match.groups()
        return cls._create_ingredient(quantity_str, unit.strip(), name.strip())
    
    @classmethod
    def _create_ingredient(cls, quantity_str: str, unit: str, name: str) -> Ingredient:
        """Create an Ingredient object from parsed components."""
        # Handle fractions
        if '/' in quantity_str:
            parts = quantity_str.split('/')
            if len(parts) == 2:
                try:
                    numerator = Decimal(parts[0])
                    denominator = Decimal(parts[1])
                    quantity = numerator / denominator
                except (ValueError, ZeroDivisionError):
                    quantity = Decimal(1)
            else:
                quantity = Decimal(1)
        else:
            try:
                quantity = Decimal(quantity_str)
            except ValueError:
                quantity = Decimal(1)
        
        # Normalize unit (singular form)
        unit = unit.lower().strip()
        if unit in cls.UNITS:
            # Convert to singular form for common units
            unit_mapping = {
                'cups': 'cup', 'tbsps': 'tbsp', 'tablespoons': 'tablespoon',
                'tsps': 'tsp', 'teaspoons': 'teaspoon', 'ounces': 'ounce',
                'pounds': 'pound', 'grams': 'gram', 'kilograms': 'kilogram',
                'milliliters': 'milliliter', 'liters': 'liter',
                'fluid ounces': 'fluid ounce', 'cloves': 'clove',
                'bunches': 'bunch', 'cans': 'can', 'jars': 'jar',
                'packages': 'package'
            }
            unit = unit_mapping.get(unit, unit)
        
        return Ingredient(quantity=quantity, unit=unit, name=name)


def display_recipe(recipe: Recipe) -> None:
    """Display a recipe in a formatted way."""
    click.echo(f"\n{'='*50}")
    click.echo(f"Recipe: {recipe.name}")
    click.echo(f"Servings: {recipe.original_servings}")
    click.echo(f"{'='*50}")
    
    click.echo("\nIngredients:")
    for i, ingredient in enumerate(recipe.ingredients, 1):
        click.echo(f"  {i}. {ingredient}")
    
    if recipe.instructions:
        click.echo("\nInstructions:")
        for i, instruction in enumerate(recipe.instructions, 1):
            click.echo(f"  {i}. {instruction}")
    
    click.echo(f"{'='*50}\n")


def get_recipe_from_user() -> Recipe:
    """Interactive function to get recipe input from user."""
    click.echo("Enter your recipe details:")
    
    name = click.prompt("Recipe name", default="My Recipe")
    
    while True:
        try:
            original_servings = click.prompt("Original number of servings", type=int)
            if original_servings > 0:
                break
            else:
                click.echo("Please enter a positive number.")
        except ValueError:
            click.echo("Please enter a valid number.")
    
    click.echo("\nEnter ingredients (one per line, format: 'quantity unit name')")
    click.echo("Examples: '2 cups flour', '1/2 tsp salt', '3 large eggs'")
    click.echo("Press Enter twice when done:")
    
    ingredients = []
    while True:
        line = click.prompt("Ingredient", default="", show_default=False)
        if not line:
            break
        
        ingredient = RecipeParser.parse_ingredient_line(line)
        if ingredient:
            ingredients.append(ingredient)
        else:
            click.echo(f"Could not parse: '{line}'. Please use format: 'quantity unit name'")
    
    if not ingredients:
        click.echo("No valid ingredients entered. Using sample recipe.")
        ingredients = [
            Ingredient(Decimal('2'), 'cups', 'all-purpose flour'),
            Ingredient(Decimal('1'), 'tsp', 'salt'),
            Ingredient(Decimal('1'), 'cup', 'water'),
            Ingredient(Decimal('2'), 'tbsp', 'olive oil')
        ]
    
    return Recipe(name=name, original_servings=original_servings, ingredients=ingredients)


@click.command()
@click.option('--original-servings', '-o', type=int, help='Original number of servings')
@click.option('--new-servings', '-n', type=int, help='New number of servings')
@click.option('--interactive', '-i', is_flag=True, help='Run in interactive mode')
def main(original_servings: Optional[int], new_servings: Optional[int], interactive: bool) -> None:
    """Recipe Scaler - Scale recipes from one serving size to another.
    
    This program allows you to scale recipes from one serving size to another
    while maintaining proper proportions. You can use it in interactive mode
    to enter your own recipe, or use command line options for quick scaling.
    
    Examples:
        $ python main.py --interactive
        $ python main.py --original-servings 4 --new-servings 100
        $ python main.py -o 4 -n 100
    """
    
    if interactive or (original_servings is None and new_servings is None):
        # Interactive mode
        recipe = get_recipe_from_user()
        
        target_servings: int = 0
        while True:
            try:
                new_servings_input = click.prompt(
                    f"Scale to how many servings? (original: {recipe.original_servings})", 
                    type=int
                )
                if new_servings_input > 0:
                    target_servings = new_servings_input
                    break
                else:
                    click.echo("Please enter a positive number.")
            except ValueError:
                click.echo("Please enter a valid number.")
        
        scaled_recipe = recipe.scale_to_servings(target_servings)
        display_recipe(scaled_recipe)
        
    else:
        # Command line mode
        if original_servings is None or new_servings is None:
            click.echo("Error: Both --original-servings and --new-servings are required for non-interactive mode.")
            click.echo("Use --interactive for interactive mode.")
            return
        
        if original_servings <= 0 or new_servings <= 0:
            click.echo("Error: Number of servings must be positive.")
            return
        
        # For command line mode, use a sample recipe
        sample_recipe = Recipe(
            name="Sample Recipe",
            original_servings=original_servings,
            ingredients=[
                Ingredient(Decimal('2'), 'cups', 'all-purpose flour'),
                Ingredient(Decimal('1'), 'tsp', 'salt'),
                Ingredient(Decimal('1'), 'cup', 'water'),
                Ingredient(Decimal('2'), 'tbsp', 'olive oil')
            ]
        )
        
        scaled_recipe = sample_recipe.scale_to_servings(new_servings)
        display_recipe(scaled_recipe)


if __name__ == "__main__":
    main()
