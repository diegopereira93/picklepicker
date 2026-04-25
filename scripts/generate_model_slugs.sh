#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

DB_URL="${1:-$DATABASE_URL}"

if [ -z "$DB_URL" ] && [ -f "$ENV_FILE" ]; then
  DB_URL=$(grep -E '^DATABASE_URL=' "$ENV_FILE" | head -1 | cut -d'=' -f2-)
fi

if [ -z "$DB_URL" ]; then
    echo "Error: DATABASE_URL not found. Set it in .env, export as env var, or pass as argument."
    exit 1
fi

run_sql_file() {
  local sql_file="$1"
  if command -v psql &>/dev/null; then
    psql "$DB_URL" -f "$sql_file"
  else
    docker compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T postgres psql "$DB_URL" -f /dev/stdin < "$sql_file"
  fi
}

run_sql_query() {
  local query="$1"
  if command -v psql &>/dev/null; then
    psql "$DB_URL" -c "$query"
  else
    echo "$query" | docker compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T postgres psql "$DB_URL"
  fi
}

echo "Generating model_slug for paddles with NULL slugs..."
run_sql_file "$SCRIPT_DIR/generate_model_slugs.sql"
echo "Done. Checking for remaining NULLs..."
run_sql_query "SELECT COUNT(*) AS remaining_nulls FROM paddles WHERE model_slug IS NULL;"
