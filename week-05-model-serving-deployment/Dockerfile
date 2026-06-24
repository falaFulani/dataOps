# =============================================================================
# Model Serving Dockerfile
# =============================================================================
# This is a standard production Dockerfile. If you've built containers for
# Java/Go/Node services, this is the same pattern:
# - Multi-stage build (keep final image small)
# - Non-root user (security)
# - Health check (orchestrator integration)
# - Pinned base image (reproducibility)
#
# The only "ML-specific" detail: we copy the model artifact into the image.
# In production, you might pull from a model registry at startup instead.
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Build dependencies
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: Production image
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS production

# Metadata labels (same as your other service images)
LABEL maintainer="Alex Mashua"
LABEL service="ml-model-service"
LABEL version="1.0.0"
LABEL description="Iris model serving API"

# Security: run as non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app/ ./app/

# Train the model during build (so the artifact is baked into the image)
# In production, you'd pull this from a model registry instead
RUN python -m app.model_training

# Switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose the API port
EXPOSE 8000

# Health check — same as any other service container
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run with uvicorn (production ASGI server)
# --workers: scale with CPU cores (same as gunicorn workers for Flask)
# --host 0.0.0.0: listen on all interfaces (required in containers)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
