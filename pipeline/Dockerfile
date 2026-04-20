FROM python:3.12-slim

WORKDIR /app

# Install system deps for psycopg binary
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy pipeline source and install as package
COPY pipeline/ ./pipeline/
RUN pip install --no-cache-dir ./pipeline

# Ensure 'from pipeline.xxx' imports work from /app
ENV PYTHONPATH=/app

WORKDIR /app/pipeline

# Default: show help
CMD ["python", "-c", "print('Usage: docker compose run --rm pipeline python -m crawlers.<name>')"]
