#!/usr/bin/env python3
"""
Recipe Scaler - A Python program to scale recipes from one serving size to another.

This program allows you to input a recipe with ingredients and their quantities,
then scale it to a different number of servings while maintaining proper proportions.
"""

import re
import argparse
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
    print(f"\n{'='*50}")
    print(f"Recipe: {recipe.name}")
    print(f"Servings: {recipe.original_servings}")
    print(f"{'='*50}")
    
    print("\nIngredients:")
    for i, ingredient in enumerate(recipe.ingredients, 1):
        print(f"  {i}. {ingredient}")
    
    if recipe.instructions:
        print("\nInstructions:")
        for i, instruction in enumerate(recipe.instructions, 1):
            print(f"  {i}. {instruction}")
    
    print(f"{'='*50}\n")


def get_recipe_from_user() -> Recipe:
    """Interactive function to get recipe input from user."""
    print("Enter your recipe details:")
    
    name = input("Recipe name: ").strip()
    if not name:
        name = "My Recipe"
    
    while True:
        try:
            original_servings = int(input("Original number of servings: "))
            if original_servings > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    print("\nEnter ingredients (one per line, format: 'quantity unit name')")
    print("Examples: '2 cups flour', '1/2 tsp salt', '3 large eggs'")
    print("Press Enter twice when done:")
    
    ingredients = []
    while True:
        line = input("Ingredient: ").strip()
        if not line:
            break
        
        ingredient = RecipeParser.parse_ingredient_line(line)
        if ingredient:
            ingredients.append(ingredient)
        else:
            print(f"Could not parse: '{line}'. Please use format: 'quantity unit name'")
    
    if not ingredients:
        print("No valid ingredients entered. Using sample recipe.")
        ingredients = [
            Ingredient(Decimal('2'), 'cups', 'all-purpose flour'),
            Ingredient(Decimal('1'), 'tsp', 'salt'),
            Ingredient(Decimal('1'), 'cup', 'water'),
            Ingredient(Decimal('2'), 'tbsp', 'olive oil')
        ]
    
    return Recipe(name=name, original_servings=original_servings, ingredients=ingredients)


def main() -> None:
    """Main function to run the recipe scaler."""
    parser = argparse.ArgumentParser(
        description="Recipe Scaler - Scale recipes from one serving size to another"
    )
    parser.add_argument(
        '--original-servings', '-o', 
        type=int, 
        help='Original number of servings'
    )
    parser.add_argument(
        '--new-servings', '-n', 
        type=int, 
        help='New number of servings'
    )
    parser.add_argument(
        '--interactive', '-i', 
        action='store_true', 
        help='Run in interactive mode'
    )
    
    args = parser.parse_args()
    
    if args.interactive or (args.original_servings is None and args.new_servings is None):
        # Interactive mode
        recipe = get_recipe_from_user()
        
        while True:
            try:
                new_servings = int(input(f"Scale to how many servings? (original: {recipe.original_servings}): "))
                if new_servings > 0:
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")
        
        scaled_recipe = recipe.scale_to_servings(new_servings)
        display_recipe(scaled_recipe)
        
    else:
        # Command line mode
        if args.original_servings is None or args.new_servings is None:
            print("Error: Both --original-servings and --new-servings are required for non-interactive mode.")
            print("Use --interactive for interactive mode.")
            return
        
        if args.original_servings <= 0 or args.new_servings <= 0:
            print("Error: Number of servings must be positive.")
            return
        
        # For command line mode, use a sample recipe
        sample_recipe = Recipe(
            name="Sample Recipe",
            original_servings=args.original_servings,
            ingredients=[
                Ingredient(Decimal('2'), 'cups', 'all-purpose flour'),
                Ingredient(Decimal('1'), 'tsp', 'salt'),
                Ingredient(Decimal('1'), 'cup', 'water'),
                Ingredient(Decimal('2'), 'tbsp', 'olive oil')
            ]
        )
        
        scaled_recipe = sample_recipe.scale_to_servings(args.new_servings)
        display_recipe(scaled_recipe)


if __name__ == "__main__":
    main()
