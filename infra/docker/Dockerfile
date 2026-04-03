# Multi-stage Dockerfile for Jira AI Agent

# Base stage
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Dependencies stage
FROM base as dependencies

WORKDIR /app

# Copy requirements
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Development stage
FROM dependencies as development

# Install development dependencies
RUN pip install pytest pytest-asyncio pytest-cov black flake8 mypy pre-commit

# Copy source code
COPY . .

# Set up development environment
RUN python -m pip install -e .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM dependencies as production

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Worker stage (for background processing)
FROM production as worker

# Override CMD for worker
CMD ["python", "-m", "app.workers.ticket_worker"]

# Ingestion stage (for Confluence ingestion)
FROM production as ingestion

# Override CMD for ingestion
CMD ["python", "-m", "app.ingestion.ingest"]
