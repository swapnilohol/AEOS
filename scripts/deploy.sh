#!/usr/bin/env bash
# Deploys the latest code to this VPS.
# Usage: ./scripts/deploy.sh
#
# Assumes: repo already cloned, .env already configured, and
# scripts/init_letsencrypt.sh already run once for this domain.

set -euo pipefail

COMPOSE="docker compose -f docker-compose.yml -f docker-compose.production.yml"

echo "==> Pulling latest code"
git pull --ff-only

echo "==> Building images"
$COMPOSE build

echo "==> Starting/updating services"
$COMPOSE up -d

echo "==> Running database migrations"
$COMPOSE exec -T backend alembic upgrade head

echo "==> Seeding baseline reference data (idempotent)"
$COMPOSE exec -T backend python -m app.db.seed

echo "==> Pruning unused images"
docker image prune -f

echo "==> Deployment complete. Checking health..."
./scripts/health_check.sh
