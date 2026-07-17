#!/usr/bin/env bash
# Runs Alembic migrations and seeds baseline reference data.
# Usage: ./scripts/migrate_and_seed.sh

set -euo pipefail

echo "Running Alembic migrations..."
docker compose exec backend alembic upgrade head

echo "Seeding baseline data..."
docker compose exec backend python -m app.db.seed

echo "Done."
