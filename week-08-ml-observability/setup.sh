#!/usr/bin/env bash
# ==============================================================================
# Week 8: ML Observability — Setup Script
# ==============================================================================
# Verifies prerequisites and starts the observability stack.
#
# Prerequisites:
#   - Docker (with docker compose plugin)
#
# Usage:
#   chmod +x setup.sh
#   ./setup.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=============================================="
echo " Week 8: ML Observability — Setup"
echo "=============================================="
echo ""

CHECKS_PASSED=0
CHECKS_TOTAL=0

check() {
    local name="$1"
    local command="$2"
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))

    if eval "$command" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $name"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "  ${RED}✗${NC} $name"
        return 1
    fi
}

# ---------------------------------------------------------------------------
# Check prerequisites
# ---------------------------------------------------------------------------
echo "Checking prerequisites..."
echo ""

FAILED=0

check "Docker installed" "docker --version" || FAILED=1
check "Docker daemon running" "docker info" || FAILED=1
check "Docker Compose available" "docker compose version" || FAILED=1

echo ""

if [ $FAILED -ne 0 ]; then
    echo -e "${RED}Prerequisites check failed.${NC}"
    echo ""
    echo "Please install/start the missing tools:"
    echo "  - Docker Desktop: https://docs.docker.com/get-docker/"
    echo "  - Docker Compose is included with Docker Desktop"
    echo ""
    exit 1
fi

echo -e "${GREEN}All prerequisites satisfied ($CHECKS_PASSED/$CHECKS_TOTAL).${NC}"
echo ""

# ---------------------------------------------------------------------------
# Check for port conflicts
# ---------------------------------------------------------------------------
echo "Checking port availability..."
echo ""

check_port() {
    local port="$1"
    local service="$2"
    if lsof -i ":$port" > /dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠${NC}  Port $port is in use (needed for $service)"
        return 1
    else
        echo -e "  ${GREEN}✓${NC} Port $port available ($service)"
        return 0
    fi
}

PORT_CONFLICT=0
check_port 8000 "Model Service" || PORT_CONFLICT=1
check_port 9090 "Prometheus" || PORT_CONFLICT=1
check_port 3000 "Grafana" || PORT_CONFLICT=1

echo ""

if [ $PORT_CONFLICT -ne 0 ]; then
    echo -e "${YELLOW}Warning: Some ports are already in use.${NC}"
    echo "Stop the conflicting services or modify docker-compose.yml port mappings."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
# Start the stack
# ---------------------------------------------------------------------------
echo "Starting the ML Observability stack..."
echo ""

docker compose up -d --build

echo ""
echo -e "${GREEN}=============================================="
echo " Stack is running!"
echo "==============================================${NC}"
echo ""
echo "  Model Service:  http://localhost:8000"
echo "  Prometheus:     http://localhost:9090"
echo "  Grafana:        http://localhost:3000  (admin/admin)"
echo ""
echo "Quick test — generate some predictions:"
echo ""
echo '  for i in $(seq 1 20); do'
echo '    curl -s -X POST http://localhost:8000/predict \'
echo '      -H "Content-Type: application/json" \'
echo "      -d '{\"features\": [5.1, 3.5, 1.4, 0.2]}' > /dev/null"
echo '  done'
echo ""
echo "Then open Grafana → 'ML Observability' dashboard to see both layers."
echo ""
echo "To stop:  docker compose down"
echo "To clean: docker compose down -v  (removes stored metrics data)"
