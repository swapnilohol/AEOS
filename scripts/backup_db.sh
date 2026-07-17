#!/usr/bin/env bash
# Logical (pg_dump) backup of the Postgres database, with pruning of old
# backups. Suggested cron (documented, not auto-installed):
#   0 3 * * * cd /path/to/AI-Engineering-OS && ./scripts/backup_db.sh
#
# Chosen over raw volume snapshots because pg_dump backups are portable,
# human-inspectable, and restorable into any Postgres version-compatible
# instance — appropriate for a single-VPS MVP (Global Rule: simplicity).

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
COMPOSE="docker compose -f docker-compose.yml -f docker-compose.production.yml"

if [ -f .env ]; then
    # shellcheck disable=SC1091
    source .env
fi

mkdir -p "$BACKUP_DIR"
timestamp="$(date +%Y%m%d_%H%M%S)"
backup_file="$BACKUP_DIR/aeos_db_${timestamp}.sql.gz"

echo "==> Dumping database to $backup_file"
$COMPOSE exec -T postgres pg_dump -U "${POSTGRES_USER:-aeos_user}" "${POSTGRES_DB:-aeos_db}" | gzip > "$backup_file"

echo "==> Pruning backups older than ${RETENTION_DAYS} days"
find "$BACKUP_DIR" -name "aeos_db_*.sql.gz" -mtime "+${RETENTION_DAYS}" -delete

echo "==> Backup complete: $backup_file"
