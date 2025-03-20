#!/bin/bash
# Script to install dependencies using UV

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "UV is not installed. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create or update virtual environment
echo "Creating/updating virtual environment with UV..."
uv venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies from pyproject.toml
echo "Installing dependencies from pyproject.toml..."
uv pip install -e .

echo "Dependencies installed successfully!"
echo "To activate the virtual environment, run: source .venv/bin/activate" 