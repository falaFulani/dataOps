#!/bin/bash
# Week 1 — Environment setup
# Run this once to create a virtual environment and install dependencies

set -e

echo "=== Setting up Week 1 environment ==="

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
pip install scikit-learn pandas matplotlib jupyter joblib

echo ""
echo "=== Setup complete ==="
echo ""
echo "To get started:"
echo "  source venv/bin/activate"
echo "  jupyter notebook lab-train-simple-model.ipynb"
echo ""
echo "Or if you prefer VS Code:"
echo "  Open lab-train-simple-model.ipynb in VS Code (it handles Jupyter natively)"
