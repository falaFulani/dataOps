#!/usr/bin/env bash
# =============================================================================
# Setup Script - Week 5: Model Serving & Deployment
# =============================================================================
# Installs Python dependencies for the model serving lab.
#
# Usage:
#   chmod +x setup.sh
#   ./setup.sh
# =============================================================================

set -euo pipefail

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Week 5: Model Serving & Deployment - Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_CMD=""

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.9+ first."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "  Found: $PYTHON_CMD ($PYTHON_VERSION)"

# Check pip
echo ""
echo "Checking pip..."
PIP_CMD=""

if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
elif $PYTHON_CMD -m pip --version &> /dev/null; then
    PIP_CMD="$PYTHON_CMD -m pip"
else
    echo "❌ pip not found. Please install pip first."
    exit 1
fi

echo "  Found: $PIP_CMD"

# Create virtual environment (recommended)
echo ""
echo "Creating virtual environment..."
VENV_DIR=".venv"

if [ -d "$VENV_DIR" ]; then
    echo "  Virtual environment already exists at $VENV_DIR"
else
    $PYTHON_CMD -m venv "$VENV_DIR"
    echo "  Created virtual environment at $VENV_DIR"
fi

# Activate virtual environment
echo "  Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt --quiet

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Installed packages:"
pip list --format=columns | grep -E "(fastapi|uvicorn|scikit-learn|pandas|joblib|pydantic|numpy|httpx)"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment: source .venv/bin/activate"
echo "  2. Train the model: python app/model_training.py"
echo "  3. Start the server: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "  4. Test the API: ./test_api.sh"
echo ""
echo "Or use Docker:"
echo "  docker-compose up --build"
echo ""
