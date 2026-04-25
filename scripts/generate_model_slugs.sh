#!/bin/bash
# Generate model_slug for all paddles with NULL slugs
# Usage: ./scripts/generate_model_slugs.sh [DATABASE_URL]

set -e
DB_URL="${1:-$DATABASE_URL}"

if [ -z "$DB_URL" ]; then
    echo "Error: DATABASE_URL not set. Pass it as argument or set env var."
    exit 1
fi

echo "Generating model_slug for paddles with NULL slugs..."
psql "$DB_URL" -f "$(dirname "$0")/generate_model_slugs.sql"
echo "Done. Checking for remaining NULLs..."
psql "$DB_URL" -c "SELECT COUNT(*) AS remaining_nulls FROM paddles WHERE model_slug IS NULL;"
