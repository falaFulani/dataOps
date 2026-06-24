#!/bin/bash
# Week 6 — ML Pipeline & Orchestration Environment Setup
# Run this once to create a virtual environment and install dependencies

set -e

echo "=== Setting up Week 6: ML Pipelines & Orchestration ==="
echo ""

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

echo ""
echo "Installing dependencies..."
echo "  - prefect        (pipeline orchestrator — like Jenkins/Argo for ML)"
echo "  - scikit-learn   (ML library for training)"
echo "  - pandas         (data manipulation)"
echo "  - pyyaml         (config file parsing)"
echo "  - joblib         (model serialization)"
echo ""

pip install prefect scikit-learn pandas pyyaml joblib

echo ""
echo "=== Setup complete ==="
echo ""
echo "Installed versions:"
python -c "import prefect; print(f'  Prefect:      {prefect.__version__}')"
python -c "import sklearn; print(f'  scikit-learn:  {sklearn.__version__}')"
python -c "import pandas; print(f'  pandas:        {pandas.__version__}')"
python -c "import yaml; print(f'  PyYAML:        {yaml.__version__}')"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  To run the ML pipeline:"
echo ""
echo "    source venv/bin/activate"
echo "    python pipeline.py"
echo ""
echo "  To see the Prefect dashboard (optional):"
echo ""
echo "    prefect server start"
echo "    # Then open http://127.0.0.1:4200 in your browser"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
