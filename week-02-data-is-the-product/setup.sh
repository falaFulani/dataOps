#!/bin/bash
# Week 2 — Environment setup
# Run this once to create a virtual environment and install dependencies

set -e

echo "=== Setting up Week 2 environment ==="

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate and install
source venv/bin/activate

pip install --upgrade pip
pip install \
    scikit-learn \
    pandas \
    numpy \
    great-expectations \
    matplotlib \
    jupyter \
    joblib

echo ""
echo "=== Setup complete ==="
echo ""
echo "To get started:"
echo "  source venv/bin/activate"
echo "  jupyter notebook lab-data-validation.ipynb"
echo ""
echo "Or if you prefer VS Code:"
echo "  Open lab-data-validation.ipynb in VS Code (it handles Jupyter natively)"
echo ""
echo "Note: Great Expectations is installed but the lab uses plain pandas for"
echo "validation checks first. GE is available if you want to explore it further."
