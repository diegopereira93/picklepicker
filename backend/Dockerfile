FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/backend

# Install system dependencies for psycopg (binary wheels need libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first (layer cache)
COPY backend/pyproject.toml ./pyproject.toml

# Install Python dependencies
RUN pip install --no-cache-dir .

# Copy backend source
COPY backend/ .

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Railway sets PORT dynamically, default to 8000
EXPOSE ${PORT:-8000}

# Start FastAPI (matches railway.toml [start] cmd)
# Working directory is /app/backend, so app.main:app is the correct module path
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
