#!/usr/bin/env bash
# Restores the database from a backup produced by scripts/backup_db.sh.
# Usage: ./scripts/restore_db.sh backups/aeos_db_20260101_030000.sql.gz
#
# WARNING: this drops and recreates all data in the target database.

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <path-to-backup.sql.gz>"
    exit 1
fi

BACKUP_FILE="$1"
if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: backup file not found: $BACKUP_FILE"
    exit 1
fi

if [ -f .env ]; then
    # shellcheck disable=SC1091
    source .env
fi

COMPOSE="docker compose -f docker-compose.yml -f docker-compose.production.yml"
POSTGRES_USER="${POSTGRES_USER:-aeos_user}"
POSTGRES_DB="${POSTGRES_DB:-aeos_db}"

read -r -p "This will OVERWRITE the current database '$POSTGRES_DB'. Continue? [y/N] " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Aborted."
    exit 1
fi

echo "==> Restoring $BACKUP_FILE into $POSTGRES_DB"
gunzip -c "$BACKUP_FILE" | $COMPOSE exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"

echo "==> Restore complete."
