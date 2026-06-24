#!/usr/bin/env bash
# =============================================================================
# Deploy Model Service to Local Kubernetes Cluster
# =============================================================================
# This script:
# 1. Creates a kind cluster (if it doesn't exist)
# 2. Builds and loads the model service image
# 3. Installs NGINX Ingress Controller
# 4. Creates the namespace and deploys all manifests
# 5. Waits for rollout and verifies the deployment
#
# Prerequisites: Run ./setup.sh first to verify tools are installed.
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

CLUSTER_NAME="mlops-lab"
NAMESPACE="ml-serving"
IMAGE_NAME="model-service"
IMAGE_TAG="latest"
WEEK5_DIR="../week-05-model-serving-deployment"

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# -----------------------------------------------------------------------------
# Step 1: Create kind cluster (if needed)
# -----------------------------------------------------------------------------
create_cluster() {
    info "Checking for existing kind cluster '${CLUSTER_NAME}'..."

    if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
        ok "Cluster '${CLUSTER_NAME}' already exists"
        kubectl cluster-info --context "kind-${CLUSTER_NAME}" > /dev/null 2>&1 || \
            error "Cluster exists but is not reachable. Try: kind delete cluster --name ${CLUSTER_NAME}"
        return
    fi

    info "Creating kind cluster '${CLUSTER_NAME}' with Ingress support..."

    # Kind config with port mappings for Ingress
    cat <<EOF | kind create cluster --name "${CLUSTER_NAME}" --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    kubeadmConfigPatches:
      - |
        kind: InitConfiguration
        nodeRegistration:
          kubeletExtraArgs:
            node-labels: "ingress-ready=true"
    extraPortMappings:
      - containerPort: 80
        hostPort: 80
        protocol: TCP
      - containerPort: 443
        hostPort: 443
        protocol: TCP
  - role: worker
  - role: worker
EOF

    ok "Cluster '${CLUSTER_NAME}' created (3 nodes: 1 control-plane, 2 workers)"
}

# -----------------------------------------------------------------------------
# Step 2: Build the model service image
# -----------------------------------------------------------------------------
build_image() {
    info "Building model service Docker image..."

    if [ ! -d "${WEEK5_DIR}" ]; then
        error "Week 5 directory not found at ${WEEK5_DIR}. Cannot build image."
    fi

    docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" "${WEEK5_DIR}"
    ok "Built ${IMAGE_NAME}:${IMAGE_TAG}"

    # Load image into kind cluster (kind uses its own container registry)
    info "Loading image into kind cluster..."
    kind load docker-image "${IMAGE_NAME}:${IMAGE_TAG}" --name "${CLUSTER_NAME}"
    ok "Image loaded into cluster"
}

# -----------------------------------------------------------------------------
# Step 3: Install NGINX Ingress Controller
# -----------------------------------------------------------------------------
install_ingress() {
    info "Checking for NGINX Ingress Controller..."

    if kubectl get namespace ingress-nginx > /dev/null 2>&1; then
        if kubectl get pods -n ingress-nginx -l app.kubernetes.io/component=controller --field-selector=status.phase=Running 2>/dev/null | grep -q "Running"; then
            ok "NGINX Ingress Controller already running"
            return
        fi
    fi

    info "Installing NGINX Ingress Controller for kind..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

    info "Waiting for Ingress Controller to be ready (this may take 1-2 minutes)..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=120s

    ok "NGINX Ingress Controller is ready"
}

# -----------------------------------------------------------------------------
# Step 4: Create namespace and deploy manifests
# -----------------------------------------------------------------------------
deploy_manifests() {
    info "Creating namespace '${NAMESPACE}'..."
    kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

    # Create a minimal service account
    info "Creating service account..."
    kubectl create serviceaccount model-service -n "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

    info "Deploying model service manifests..."
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml
    kubectl apply -f k8s/hpa.yaml
    kubectl apply -f k8s/ingress.yaml

    ok "All manifests applied"
}

# -----------------------------------------------------------------------------
# Step 5: Wait for rollout and verify
# -----------------------------------------------------------------------------
verify_deployment() {
    info "Waiting for deployment rollout..."
    kubectl rollout status deployment/model-service -n "${NAMESPACE}" --timeout=120s

    echo ""
    ok "Deployment successful!"
    echo ""

    info "Cluster status:"
    echo "───────────────────────────────────────────────────────────"
    kubectl get pods -n "${NAMESPACE}" -o wide
    echo ""
    kubectl get svc -n "${NAMESPACE}"
    echo ""
    kubectl get hpa -n "${NAMESPACE}"
    echo ""
    kubectl get ingress -n "${NAMESPACE}"
    echo "───────────────────────────────────────────────────────────"

    echo ""
    info "Testing the service via port-forward..."
    echo ""

    # Quick port-forward test
    kubectl port-forward svc/model-service -n "${NAMESPACE}" 8080:80 &
    PF_PID=$!
    sleep 3

    # Test health endpoint
    if curl -s http://localhost:8080/health | grep -q "healthy"; then
        ok "Health check passed ✓"
    else
        warn "Health check didn't respond (pod may still be starting)"
    fi

    # Test prediction endpoint
    RESPONSE=$(curl -s -X POST http://localhost:8080/predict \
        -H "Content-Type: application/json" \
        -d '{"features": [5.1, 3.5, 1.4, 0.2]}' 2>/dev/null || echo "")

    if echo "${RESPONSE}" | grep -q "prediction"; then
        ok "Prediction endpoint working ✓"
        echo "    Response: ${RESPONSE}"
    else
        warn "Prediction endpoint didn't respond (pod may still be loading model)"
        echo "    Try manually: kubectl port-forward svc/model-service -n ${NAMESPACE} 8080:80"
        echo "    Then: curl -X POST http://localhost:8080/predict -H 'Content-Type: application/json' -d '{\"features\": [5.1, 3.5, 1.4, 0.2]}'"
    fi

    # Clean up port-forward
    kill ${PF_PID} 2>/dev/null || true

    echo ""
    echo "───────────────────────────────────────────────────────────"
    info "Access via Ingress:"
    echo "    1. Add to /etc/hosts: 127.0.0.1 model.local"
    echo "    2. curl http://model.local/health"
    echo "    3. curl -X POST http://model.local/predict \\"
    echo "         -H 'Content-Type: application/json' \\"
    echo "         -d '{\"features\": [5.1, 3.5, 1.4, 0.2]}'"
    echo ""
    info "Or use port-forward:"
    echo "    kubectl port-forward svc/model-service -n ${NAMESPACE} 8080:80"
    echo "───────────────────────────────────────────────────────────"
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Week 7: Deploy Model Service to Kubernetes                  ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

create_cluster
build_image
install_ingress
deploy_manifests
verify_deployment

echo ""
ok "Done! Your model is serving predictions on Kubernetes."
echo ""
