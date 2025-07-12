# Recipe Scaler

A Python program that scales recipes from one serving size to another while maintaining proper proportions.

## Features

- **Interactive Mode**: Enter your recipe ingredients and scale them interactively
- **Command Line Mode**: Scale recipes using command line arguments
- **Smart Parsing**: Automatically parses ingredient lines with quantities, units, and names
- **Fraction Support**: Handles fractions like "1/2", "3/4" in ingredient quantities
- **Unit Normalization**: Converts plural units to singular form for consistency
- **Precise Calculations**: Uses Decimal arithmetic for accurate scaling

## Installation

1. Make sure you have Python 3.13+ installed
2. No additional dependencies required - uses only Python standard library

## Usage

### Interactive Mode (Recommended)

Run the program without arguments to enter interactive mode:

```bash
python main.py
```

You'll be prompted to:
1. Enter the recipe name
2. Specify the original number of servings
3. Enter ingredients one by one (format: "quantity unit name")
4. Specify the new number of servings

Example interaction:
```
Enter your recipe details:
Recipe name: Chocolate Chip Cookies
Original number of servings: 4

Enter ingredients (one per line, format: 'quantity unit name')
Examples: '2 cups flour', '1/2 tsp salt', '3 large eggs'
Press Enter twice when done:
Ingredient: 2 cups all-purpose flour
Ingredient: 1/2 tsp salt
Ingredient: 1 cup butter
Ingredient: 3/4 cup sugar
Ingredient: 2 large eggs
Ingredient: 1 cup chocolate chips
Ingredient: 

Scale to how many servings? (original: 4): 100
```

### Command Line Mode

Use command line arguments for quick scaling:

```bash
python main.py --original-servings 4 --new-servings 100
```

Or with short options:
```bash
python main.py -o 4 -n 100
```

### Command Line Options

- `--original-servings, -o`: Original number of servings
- `--new-servings, -n`: New number of servings  
- `--interactive, -i`: Force interactive mode
- `--help, -h`: Show help message

## Input Format

Ingredients should be entered in the format: `quantity unit name`

### Supported Formats:
- `2 cups flour`
- `1/2 tsp salt`
- `3 large eggs`
- `1.5 lbs chicken`
- `500 g pasta`
- `2 tbsp olive oil`

### Supported Units:
- Volume: cup, tbsp, tsp, ml, l, fl oz
- Weight: oz, lb, g, kg
- Count: clove, bunch, can, jar, package
- Special: pinch, dash

## Example Output

```
==================================================
Recipe: Chocolate Chip Cookies (Scaled to 100 servings)
Servings: 100
==================================================

Ingredients:
  1. 50 cups all-purpose flour
  2. 12.5 tsp salt
  3. 25 cups butter
  4. 18.75 cups sugar
  5. 50 large eggs
  6. 25 cups chocolate chips
==================================================
```

## Features

- **Accurate Scaling**: Uses precise decimal arithmetic to avoid floating-point errors
- **Smart Rounding**: Rounds quantities to 2 decimal places for readability
- **Unit Handling**: Recognizes and normalizes common cooking units
- **Fraction Support**: Handles fractions like "1/2", "3/4" automatically
- **Error Handling**: Provides helpful error messages for invalid input
- **Type Safety**: Full type hints for better code reliability

## Development

The program uses:
- **dataclasses** for clean data structures
- **argparse** for command line interface (built into Python)
- **type hints** throughout for better code quality
- **Decimal** arithmetic for precise calculations

## License

This project is licensed under the MIT License.