#!/usr/bin/env bash
# Week 3: Model Evaluation & Drift Detection — Environment Setup
# Run this script from the week-03-model-evaluation-and-drift/ directory
#
# Usage:
#   chmod +x setup.sh
#   ./setup.sh
#   source .venv/bin/activate
#   jupyter notebook lab-drift-detection.ipynb

set -euo pipefail

PYTHON_CMD=""
VENV_DIR=".venv"

echo "=========================================="
echo "Week 3: Environment Setup"
echo "=========================================="
echo ""

# Find Python 3.9+
for cmd in python3.12 python3.11 python3.10 python3.9 python3; do
    if command -v "$cmd" &> /dev/null; then
        version=$("$cmd" --version 2>&1 | awk '{print $2}')
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ]; then
            PYTHON_CMD="$cmd"
            echo "✓ Found Python: $cmd ($version)"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "✗ Error: Python 3.9+ is required but not found."
    echo "  Install Python 3.9+ and try again."
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment in ${VENV_DIR}..."
"$PYTHON_CMD" -m venv "$VENV_DIR"
echo "✓ Virtual environment created"

# Activate venv
source "${VENV_DIR}/bin/activate"
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install \
    scikit-learn==1.3.2 \
    pandas==2.1.4 \
    numpy==1.26.2 \
    evidently==0.4.13 \
    matplotlib==3.8.2 \
    jupyter==1.0.0 \
    notebook==7.0.6 \
    --quiet

echo "✓ All dependencies installed"

# Verify installation
echo ""
echo "Verifying installation..."
python -c "
import sklearn; print(f'  scikit-learn: {sklearn.__version__}')
import pandas; print(f'  pandas: {pandas.__version__}')
import numpy; print(f'  numpy: {numpy.__version__}')
import evidently; print(f'  evidently: {evidently.__version__}')
import matplotlib; print(f'  matplotlib: {matplotlib.__version__}')
"
echo "✓ All packages verified"

# Done
echo ""
echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. source ${VENV_DIR}/bin/activate"
echo "  2. jupyter notebook lab-drift-detection.ipynb"
echo ""
echo "When done, deactivate with: deactivate"
