# DatastarJinja

A FastAPI application with Jinja2 templates and Tailwind CSS.

## Setup

1. Install Python dependencies:
```bash
# If using pip
pip install -r requirements.txt

# If using uv
uv pip install -r requirements.txt
```

2. Install Node.js dependencies:
```bash
npm install
```

## Tailwind CSS

This project uses Tailwind CSS for styling:

- **Development mode**: Run `npm run dev` to watch for changes and automatically rebuild CSS
- **Build for production**: Run `npm run build` to generate an optimized, minified CSS file

When adding Tailwind classes to your HTML templates, the CSS file will automatically include only the classes you use, resulting in a minimal file size.

## Running the Application

```bash
uvicorn main:app --reload
```

Navigate to http://localhost:8000/items/1 to see the application in action.


