#!/usr/bin/env bash
# =============================================================================
# Week 7 Setup — Verify Prerequisites
# =============================================================================
# Checks that all required tools are installed and suggests installation
# commands if anything is missing.
#
# Required:
#   - docker (you have this)
#   - kubectl (you have this)
#   - kind OR minikube (for local cluster)
#
# Optional:
#   - helm (for installing ingress controller or KServe)
#   - curl (for testing endpoints)
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0

info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}  ✓${NC} $1"; }
warn()  { echo -e "${YELLOW}  ⚠${NC} $1"; }
fail()  { echo -e "${RED}  ✗${NC} $1"; ERRORS=$((ERRORS + 1)); }

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Week 7: Prerequisites Check                                  ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# -----------------------------------------------------------------------------
# Docker
# -----------------------------------------------------------------------------
info "Checking Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
    ok "Docker installed (${DOCKER_VERSION})"

    if docker info &> /dev/null; then
        ok "Docker daemon is running"
    else
        fail "Docker is installed but daemon is not running. Start Docker Desktop or dockerd."
    fi
else
    fail "Docker not found. Install: https://docs.docker.com/get-docker/"
fi

# -----------------------------------------------------------------------------
# kubectl
# -----------------------------------------------------------------------------
info "Checking kubectl..."
if command -v kubectl &> /dev/null; then
    KUBECTL_VERSION=$(kubectl version --client --short 2>/dev/null || kubectl version --client -o yaml 2>/dev/null | grep gitVersion | awk '{print $2}')
    ok "kubectl installed (${KUBECTL_VERSION})"
else
    fail "kubectl not found. Install: https://kubernetes.io/docs/tasks/tools/"
fi

# -----------------------------------------------------------------------------
# kind OR minikube
# -----------------------------------------------------------------------------
info "Checking for local k8s runtime (kind or minikube)..."
HAS_KIND=false
HAS_MINIKUBE=false

if command -v kind &> /dev/null; then
    KIND_VERSION=$(kind version 2>/dev/null | awk '{print $2}')
    ok "kind installed (${KIND_VERSION})"
    HAS_KIND=true
fi

if command -v minikube &> /dev/null; then
    MINIKUBE_VERSION=$(minikube version --short 2>/dev/null)
    ok "minikube installed (${MINIKUBE_VERSION})"
    HAS_MINIKUBE=true
fi

if [ "${HAS_KIND}" = false ] && [ "${HAS_MINIKUBE}" = false ]; then
    fail "Neither kind nor minikube found. Install one:"
    echo "       kind:     https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
    echo "                 brew install kind"
    echo "       minikube: https://minikube.sigs.k8s.io/docs/start/"
    echo "                 brew install minikube"
    echo ""
    echo "       Recommendation: kind (lighter weight, faster startup, better for CI)"
fi

# -----------------------------------------------------------------------------
# helm (optional)
# -----------------------------------------------------------------------------
info "Checking Helm (optional)..."
if command -v helm &> /dev/null; then
    HELM_VERSION=$(helm version --short 2>/dev/null)
    ok "Helm installed (${HELM_VERSION})"
else
    warn "Helm not found (optional — used for KServe/Seldon installation)"
    echo "       Install: brew install helm"
fi

# -----------------------------------------------------------------------------
# curl
# -----------------------------------------------------------------------------
info "Checking curl..."
if command -v curl &> /dev/null; then
    ok "curl available"
else
    fail "curl not found (needed for testing endpoints)"
fi

# -----------------------------------------------------------------------------
# Check Week 5 directory exists (we need the Dockerfile and app)
# -----------------------------------------------------------------------------
info "Checking Week 5 model service directory..."
WEEK5_DIR="../week-05-model-serving-deployment"

if [ -d "${WEEK5_DIR}" ]; then
    ok "Week 5 directory found at ${WEEK5_DIR}"

    if [ -f "${WEEK5_DIR}/Dockerfile" ]; then
        ok "Dockerfile present"
    else
        fail "Dockerfile not found in ${WEEK5_DIR}"
    fi

    if [ -f "${WEEK5_DIR}/app/main.py" ]; then
        ok "FastAPI app present"
    else
        fail "app/main.py not found in ${WEEK5_DIR}"
    fi
else
    fail "Week 5 directory not found at ${WEEK5_DIR}"
    echo "       The deploy script builds the image from Week 5's Dockerfile."
    echo "       Make sure you've completed Week 5 first."
fi

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo "───────────────────────────────────────────────────────────────"
if [ ${ERRORS} -eq 0 ]; then
    echo -e "${GREEN}All prerequisites met! You're ready to deploy.${NC}"
    echo ""
    echo "  Next step: ./deploy.sh"
else
    echo -e "${RED}${ERRORS} issue(s) found. Fix them before running deploy.sh${NC}"
fi
echo "───────────────────────────────────────────────────────────────"
echo ""

exit ${ERRORS}
