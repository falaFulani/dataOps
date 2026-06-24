# Week 8: Model Service with Prometheus Metrics
# ================================================
# Extends the Week 5 model service with ML observability instrumentation.
# Exposes /metrics endpoint for Prometheus alongside /predict and /health.

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Train the model at build time (simple Iris classifier)
RUN python -c "from app.main import train_model; train_model()"

EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
