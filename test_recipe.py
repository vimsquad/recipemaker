#!/usr/bin/env python3
"""
Test script to demonstrate the recipe scaler functionality.
"""

from main import Recipe, Ingredient, RecipeParser
from decimal import Decimal


def test_recipe_scaling():
    """Test the recipe scaling functionality."""
    
    # Create a sample recipe for 4 servings
    original_recipe = Recipe(
        name="Chocolate Chip Cookies",
        original_servings=4,
        ingredients=[
            Ingredient(Decimal('2'), 'cups', 'all-purpose flour'),
            Ingredient(Decimal('0.5'), 'tsp', 'salt'),
            Ingredient(Decimal('1'), 'cup', 'butter'),
            Ingredient(Decimal('0.75'), 'cup', 'sugar'),
            Ingredient(Decimal('2'), 'large', 'eggs'),
            Ingredient(Decimal('1'), 'cup', 'chocolate chips')
        ]
    )
    
    print("Original Recipe (4 servings):")
    print("=" * 50)
    for i, ingredient in enumerate(original_recipe.ingredients, 1):
        print(f"  {i}. {ingredient}")
    
    # Scale to 100 servings
    scaled_recipe = original_recipe.scale_to_servings(100)
    
    print(f"\nScaled Recipe (100 servings):")
    print("=" * 50)
    for i, ingredient in enumerate(scaled_recipe.ingredients, 1):
        print(f"  {i}. {ingredient}")
    
    # Test different scaling factors
    print(f"\nScaling Examples:")
    print("=" * 50)
    
    test_servings = [8, 12, 20, 50]
    for servings in test_servings:
        scaled = original_recipe.scale_to_servings(servings)
        print(f"\n{servings} servings:")
        for ingredient in scaled.ingredients:
            print(f"  {ingredient}")


def test_ingredient_parsing():
    """Test the ingredient parsing functionality."""
    
    test_ingredients = [
        "2 cups flour",
        "1/2 tsp salt",
        "3 large eggs",
        "1.5 lbs chicken",
        "500 g pasta",
        "2 tbsp olive oil",
        "1/4 cup milk",
        "3 cloves garlic"
    ]
    
    print("Ingredient Parsing Test:")
    print("=" * 50)
    
    for ingredient_str in test_ingredients:
        ingredient = RecipeParser.parse_ingredient_line(ingredient_str)
        if ingredient:
            print(f"'{ingredient_str}' -> {ingredient}")
        else:
            print(f"'{ingredient_str}' -> Failed to parse")


if __name__ == "__main__":
    print("Recipe Scaler Test Suite")
    print("=" * 50)
    
    print("\n1. Testing Recipe Scaling:")
    test_recipe_scaling()
    
    print("\n\n2. Testing Ingredient Parsing:")
    test_ingredient_parsing()
    
    print("\n\nTest completed!")