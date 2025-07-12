# Recipe Maker

A FastAPI-based web application for creating, managing, and sharing recipes with a beautiful web interface.

## Features

- Create and edit recipes with ingredients and instructions
- Beautiful web UI built with HTML, CSS, and JavaScript
- RESTful API for programmatic access
- Search and filter recipes
- Responsive design for mobile and desktop

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd recipemaker
```

2. Install dependencies:
```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Usage

### Web Application

Start the FastAPI server:
```bash
uvicorn recipemaker.main:app --reload
```

Then open your browser to `http://localhost:8000`

### Command Line Interface

The application also provides a CLI for quick operations:

```bash
# List all recipes
recipemaker list

# Add a new recipe
recipemaker add "Chocolate Cake" --ingredients "flour,sugar,cocoa" --instructions "Mix ingredients and bake"

# Search recipes
recipemaker search "chocolate"
```

## API Documentation

Once the server is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black recipemaker tests
isort recipemaker tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.