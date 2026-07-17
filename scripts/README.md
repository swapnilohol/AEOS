# Scripts

Operational scripts (migrations, seeding, deployment helpers) are added here
as modules are implemented.

## migrate_and_seed.sh

Runs Alembic migrations against the `backend` container, then seeds baseline
reference data (roles, pilot hackathon, 4 problems).

```
./scripts/migrate_and_seed.sh
```

Requires `docker compose up` to already be running.

## Deployment scripts (Deployment Module)

See `docs/deployment.md` for the full runbook. Summary:

- `setup_vps.sh` — one-time Ubuntu VPS bootstrap (Docker, UFW, fail2ban, swap)
- `init_letsencrypt.sh` — one-time TLS certificate issuance
- `deploy.sh` — build, migrate, restart, health-check (every deploy)
- `health_check.sh` — quick status check of frontend/backend/HTTPS
- `backup_db.sh` — gzipped `pg_dump` backup with rotation
- `restore_db.sh` — restore from a `backup_db.sh` output file
