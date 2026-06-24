#!/bin/bash
# =============================================================================
# Week 4: Experiment Tracking & Model Registry — Environment Setup
# =============================================================================
# This script installs all dependencies needed for the Week 4 lab.
# Run this before opening the Jupyter notebook.
#
# Usage:
#   chmod +x setup.sh
#   ./setup.sh
# =============================================================================

set -e

echo "=============================================="
echo "  Week 4: Experiment Tracking & Model Registry"
echo "  Setting up environment..."
echo "=============================================="
echo ""

# Check Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Found Python ${PYTHON_VERSION}"

# Create virtual environment if it doesn't exist
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✅ Virtual environment created at ./${VENV_DIR}"
else
    echo "✅ Virtual environment already exists at ./${VENV_DIR}"
fi

# Activate virtual environment
source "${VENV_DIR}/bin/activate"
echo "✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install \
    scikit-learn==1.4.2 \
    pandas==2.2.2 \
    numpy==1.26.4 \
    mlflow==2.13.0 \
    jupyter==1.0.0 \
    matplotlib==3.9.0 \
    --quiet

echo ""
echo "✅ All dependencies installed:"
echo "   - scikit-learn (ML algorithms)"
echo "   - pandas (data manipulation)"
echo "   - numpy (numerical computing)"
echo "   - mlflow (experiment tracking & model registry)"
echo "   - jupyter (notebook environment)"
echo "   - matplotlib (plotting)"

# Verify MLflow is working
echo ""
echo "🔍 Verifying MLflow installation..."
MLFLOW_VERSION=$(python3 -c "import mlflow; print(mlflow.__version__)")
echo "✅ MLflow ${MLFLOW_VERSION} is ready"

echo ""
echo "=============================================="
echo "  Setup complete! Next steps:"
echo "=============================================="
echo ""
echo "  1. Activate the venv (if not already):"
echo "     source venv/bin/activate"
echo ""
echo "  2. Start Jupyter:"
echo "     jupyter notebook lab-mlflow-tracking.ipynb"
echo ""
echo "  3. (Optional) Start MLflow UI in a separate terminal:"
echo "     source venv/bin/activate"
echo "     mlflow ui --port 5000"
echo "     Then open: http://localhost:5000"
echo ""
echo "=============================================="
