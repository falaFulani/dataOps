#!/bin/bash
# =============================================================================
# Week 9 — ML SLOs & Alerting: Environment Setup
# =============================================================================
# Installs Python dependencies for the error budget calculator.
# Lightweight — just PyYAML for parsing and standard library for everything else.
# =============================================================================

set -euo pipefail

echo "============================================"
echo "  Week 9 — ML SLOs & Alerting Setup"
echo "============================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Please install Python 3.9+."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python found: ${PYTHON_VERSION}"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "→ Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate and install dependencies
echo "→ Installing dependencies..."
source venv/bin/activate

pip install --upgrade pip --quiet
pip install pyyaml --quiet

echo "✓ Dependencies installed"
echo ""
echo "============================================"
echo "  Setup complete!"
echo "============================================"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run the error budget calculator:"
echo "  python error-budget-calculator.py"
echo "  python error-budget-calculator.py --help"
echo ""
echo "Example scenarios:"
echo "  python error-budget-calculator.py --slo-target 0.90 --window-days 30"
echo "  python error-budget-calculator.py --slo-target 0.95 --window-days 7 --breach-hours 4"
echo "  python error-budget-calculator.py --slo-target 0.90 --window-days 30 --current-value 0.87 --breach-hours 18"
echo ""
