# MLOps Capstone — Project Orchestration
# ==========================================
# This Makefile orchestrates the full MLOps system.
# Run `make help` to see all available targets.
#
# Prerequisites:
#   - Python 3.9+
#   - Docker
#   - kubectl + local k8s cluster (kind or minikube)
#   - helm (for monitoring stack)

.PHONY: help setup train serve deploy monitor test demo clean \
        setup-python setup-docker setup-k8s \
        serve-local serve-docker \
        deploy-namespace deploy-app deploy-hpa \
        monitor-prometheus monitor-grafana monitor-evidently \
        test-unit test-api test-integration \
        demo-train demo-deploy demo-traffic demo-dashboard \
        logs status port-forward

# ─── Configuration ────────────────────────────────────────────────────────────

PYTHON         := python3
VENV           := .venv
PIP            := $(VENV)/bin/pip
PYTHON_BIN     := $(VENV)/bin/python
DOCKER_IMAGE   := mlops-capstone-model
DOCKER_TAG     := latest
K8S_NAMESPACE  := mlops-capstone
K8S_CONTEXT    := kind-mlops  # or minikube
MLFLOW_URI     := http://localhost:5000
SERVING_PORT   := 8000
GRAFANA_PORT   := 3000
PROMETHEUS_PORT := 9090

# ─── Help ─────────────────────────────────────────────────────────────────────

help: ## Show this help message
	@echo "MLOps Capstone — Available targets:"
	@echo "────────────────────────────────────"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick start:"
	@echo "  make setup   → Install dependencies"
	@echo "  make demo    → Full end-to-end demonstration"

# ─── Setup ────────────────────────────────────────────────────────────────────

setup: setup-python setup-docker setup-k8s ## Install all dependencies
	@echo "✅ Setup complete. Run 'make demo' for full walkthrough."

setup-python: ## Set up Python virtual environment and dependencies
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r training/requirements.txt
	$(PIP) install -r serving/requirements.txt
	$(PIP) install -r tests/requirements.txt
	@echo "✅ Python environment ready"

setup-docker: ## Verify Docker is available
	@docker info > /dev/null 2>&1 || (echo "❌ Docker not running" && exit 1)
	@echo "✅ Docker is available"

setup-k8s: ## Verify k8s cluster is available
	@kubectl cluster-info > /dev/null 2>&1 || (echo "❌ No k8s cluster found. Run: kind create cluster --name mlops" && exit 1)
	@kubectl create namespace $(K8S_NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	@echo "✅ Kubernetes cluster ready (namespace: $(K8S_NAMESPACE))"

# ─── Training ─────────────────────────────────────────────────────────────────

train: ## Run the training pipeline (validate → train → evaluate → register)
	@echo "🚀 Starting training pipeline..."
	$(PYTHON_BIN) training/pipeline.py
	@echo "✅ Training complete. Model registered in MLflow."
	@echo "   View experiments: $(MLFLOW_URI)"

mlflow-ui: ## Start MLflow UI (background)
	$(PYTHON_BIN) -m mlflow ui --host 0.0.0.0 --port 5000 &
	@echo "📊 MLflow UI running at $(MLFLOW_URI)"

# ─── Serving ──────────────────────────────────────────────────────────────────

serve: serve-local ## Start the model service locally

serve-local: ## Run the model API locally (FastAPI + uvicorn)
	@echo "🚀 Starting model service on port $(SERVING_PORT)..."
	$(PYTHON_BIN) -m uvicorn serving.app:app --host 0.0.0.0 --port $(SERVING_PORT) --reload
	@echo "✅ Service running at http://localhost:$(SERVING_PORT)"
	@echo "   Health: http://localhost:$(SERVING_PORT)/health"
	@echo "   Docs:   http://localhost:$(SERVING_PORT)/docs"

serve-docker: ## Build and run the model service in Docker
	@echo "🐳 Building Docker image..."
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) -f serving/Dockerfile .
	@echo "🚀 Running container..."
	docker run -d --name mlops-model-server \
		-p $(SERVING_PORT):8000 \
		$(DOCKER_IMAGE):$(DOCKER_TAG)
	@echo "✅ Container running at http://localhost:$(SERVING_PORT)"

# ─── Deploy ───────────────────────────────────────────────────────────────────

deploy: deploy-namespace deploy-app deploy-hpa ## Deploy to local k8s cluster
	@echo "✅ Deployed to Kubernetes (namespace: $(K8S_NAMESPACE))"
	@echo "   Run 'make port-forward' to access locally"

deploy-namespace: ## Create/ensure k8s namespace exists
	kubectl create namespace $(K8S_NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -

deploy-app: ## Deploy model service to k8s
	@echo "🚀 Deploying model service to k8s..."
	# Load Docker image into kind cluster
	kind load docker-image $(DOCKER_IMAGE):$(DOCKER_TAG) --name mlops 2>/dev/null || true
	kubectl apply -f k8s/deployment.yml -n $(K8S_NAMESPACE)
	kubectl apply -f k8s/service.yml -n $(K8S_NAMESPACE)
	kubectl rollout status deployment/model-server -n $(K8S_NAMESPACE) --timeout=120s
	@echo "✅ Model service deployed"

deploy-hpa: ## Configure horizontal pod autoscaler
	kubectl apply -f k8s/hpa.yml -n $(K8S_NAMESPACE)
	@echo "✅ HPA configured"

port-forward: ## Forward k8s service to localhost
	@echo "🔗 Forwarding $(K8S_NAMESPACE)/model-server to localhost:$(SERVING_PORT)"
	kubectl port-forward svc/model-server $(SERVING_PORT):80 -n $(K8S_NAMESPACE)

# ─── Monitoring ───────────────────────────────────────────────────────────────

monitor: monitor-prometheus monitor-grafana monitor-evidently ## Start the full monitoring stack
	@echo "✅ Monitoring stack running"
	@echo "   Prometheus: http://localhost:$(PROMETHEUS_PORT)"
	@echo "   Grafana:    http://localhost:$(GRAFANA_PORT) (admin/admin)"
	@echo "   Evidently:  Check monitoring/evidently/ for reports"

monitor-prometheus: ## Start Prometheus
	docker-compose -f monitoring/docker-compose.yml up -d prometheus
	@echo "✅ Prometheus running on port $(PROMETHEUS_PORT)"

monitor-grafana: ## Start Grafana
	docker-compose -f monitoring/docker-compose.yml up -d grafana
	@echo "✅ Grafana running on port $(GRAFANA_PORT)"

monitor-evidently: ## Generate Evidently drift report
	$(PYTHON_BIN) monitoring/evidently/generate_report.py
	@echo "✅ Evidently report generated at monitoring/evidently/reports/"

# ─── Testing ──────────────────────────────────────────────────────────────────

test: test-unit test-api ## Run all tests
	@echo "✅ All tests passed"

test-unit: ## Run unit tests
	$(PYTHON_BIN) -m pytest tests/ -v --tb=short -k "not integration"

test-api: ## Run API tests (requires serving to be running)
	$(PYTHON_BIN) -m pytest tests/test_api.py -v --tb=short

test-integration: ## Run full integration tests (requires all services)
	$(PYTHON_BIN) -m pytest tests/ -v --tb=short -k "integration"

# ─── Demo ─────────────────────────────────────────────────────────────────────

demo: demo-train demo-deploy demo-traffic demo-dashboard ## Full end-to-end demo
	@echo ""
	@echo "══════════════════════════════════════════════════════════"
	@echo "  ✅ END-TO-END DEMO COMPLETE"
	@echo "══════════════════════════════════════════════════════════"
	@echo ""
	@echo "  What just happened:"
	@echo "  1. Trained and registered a model (MLflow)"
	@echo "  2. Containerized and deployed to Kubernetes"
	@echo "  3. Generated prediction traffic"
	@echo "  4. Monitoring stack captured metrics"
	@echo ""
	@echo "  Access points:"
	@echo "  • Model API:   http://localhost:$(SERVING_PORT)/docs"
	@echo "  • MLflow:      $(MLFLOW_URI)"
	@echo "  • Grafana:     http://localhost:$(GRAFANA_PORT)"
	@echo "  • Prometheus:  http://localhost:$(PROMETHEUS_PORT)"
	@echo ""
	@echo "  Next: Open Grafana to see operational + drift dashboards"
	@echo "══════════════════════════════════════════════════════════"

demo-train: ## Demo step: train the model
	@echo ""
	@echo "━━━ Step 1/4: Training Pipeline ━━━━━━━━━━━━━━━━━━━━━━━━"
	$(PYTHON_BIN) training/pipeline.py
	@echo "✅ Model trained and registered"

demo-deploy: ## Demo step: build and deploy
	@echo ""
	@echo "━━━ Step 2/4: Build & Deploy ━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) -f serving/Dockerfile . --quiet
	kind load docker-image $(DOCKER_IMAGE):$(DOCKER_TAG) --name mlops 2>/dev/null || true
	kubectl apply -f k8s/ -n $(K8S_NAMESPACE)
	kubectl rollout status deployment/model-server -n $(K8S_NAMESPACE) --timeout=120s
	@echo "✅ Deployed to Kubernetes"

demo-traffic: ## Demo step: generate prediction traffic
	@echo ""
	@echo "━━━ Step 3/4: Generate Traffic ━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "Sending 100 prediction requests..."
	$(PYTHON_BIN) tests/generate_traffic.py --requests 100 --endpoint http://localhost:$(SERVING_PORT)/predict
	@echo "✅ Traffic generated"

demo-dashboard: ## Demo step: show monitoring
	@echo ""
	@echo "━━━ Step 4/4: Monitoring Dashboard ━━━━━━━━━━━━━━━━━━━━━"
	docker-compose -f monitoring/docker-compose.yml up -d
	$(PYTHON_BIN) monitoring/evidently/generate_report.py
	@echo "✅ Monitoring stack running — check Grafana"

# ─── Utilities ────────────────────────────────────────────────────────────────

status: ## Show status of all components
	@echo "Component Status:"
	@echo "─────────────────"
	@echo -n "  Python env:   " && (test -d $(VENV) && echo "✅" || echo "❌ run: make setup-python")
	@echo -n "  Docker:       " && (docker info > /dev/null 2>&1 && echo "✅" || echo "❌")
	@echo -n "  K8s cluster:  " && (kubectl cluster-info > /dev/null 2>&1 && echo "✅" || echo "❌")
	@echo -n "  K8s deploy:   " && (kubectl get deploy model-server -n $(K8S_NAMESPACE) > /dev/null 2>&1 && echo "✅" || echo "❌")
	@echo -n "  Prometheus:   " && (curl -s http://localhost:$(PROMETHEUS_PORT)/-/healthy > /dev/null 2>&1 && echo "✅" || echo "❌")
	@echo -n "  Grafana:      " && (curl -s http://localhost:$(GRAFANA_PORT)/api/health > /dev/null 2>&1 && echo "✅" || echo "❌")
	@echo -n "  MLflow:       " && (curl -s $(MLFLOW_URI)/health > /dev/null 2>&1 && echo "✅" || echo "❌")

logs: ## Show logs from the model service pod
	kubectl logs -l app=model-server -n $(K8S_NAMESPACE) --tail=50 -f

# ─── Cleanup ──────────────────────────────────────────────────────────────────

clean: ## Stop and remove all resources
	@echo "🧹 Cleaning up..."
	# Stop Docker containers
	docker-compose -f monitoring/docker-compose.yml down 2>/dev/null || true
	docker rm -f mlops-model-server 2>/dev/null || true
	# Remove k8s resources
	kubectl delete namespace $(K8S_NAMESPACE) --ignore-not-found=true
	# Remove local artifacts
	rm -rf $(VENV)
	rm -rf mlruns/
	rm -rf monitoring/evidently/reports/
	rm -rf __pycache__ .pytest_cache
	@echo "✅ Cleaned up"

clean-k8s: ## Remove only k8s resources
	kubectl delete namespace $(K8S_NAMESPACE) --ignore-not-found=true
	@echo "✅ Kubernetes resources removed"

clean-docker: ## Remove only Docker resources
	docker-compose -f monitoring/docker-compose.yml down 2>/dev/null || true
	docker rm -f mlops-model-server 2>/dev/null || true
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) 2>/dev/null || true
	@echo "✅ Docker resources removed"
