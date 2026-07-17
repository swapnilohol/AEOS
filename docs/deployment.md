# Deployment Runbook

Target: a single Ubuntu 24.04 VPS (per `02_ARCHITECTURE.md`: 4 vCPU / 8GB
RAM / 80GB SSD is the recommended minimum), serving up to 10 concurrent
students.

This is deliberately a **single-VPS, Docker Compose** deployment — no
Kubernetes, no managed container platform, no multi-region setup. That
matches the project's own non-goals and "MVP first" principle.

## 1. First-time VPS setup

```
ssh youruser@your-vps-ip
git clone <your-repo-url> AI-Engineering-OS
cd AI-Engineering-OS
./scripts/setup_vps.sh
```

This installs Docker, configures UFW (only SSH/80/443 open), enables
fail2ban, and creates a swap file if none exists. Log out and back in
afterward so your user's Docker group membership takes effect.

## 2. Configure environment

```
cp .env.production.example .env
nano .env
```

Fill in real values for `DOMAIN`, `CERTBOT_EMAIL`, and every
`REPLACE_WITH_...` placeholder. Generate secrets with:

```
openssl rand -hex 32
```

`COOKIE_SECURE` must stay `true` in production (the Authentication Module
enforces HTTPS-only cookies when this is set).

## 3. Point DNS at the VPS

Create an A record for `DOMAIN` pointing at the VPS's public IP, and wait
for it to propagate before continuing (certbot's HTTP-01 challenge needs
it to resolve correctly).

## 4. Issue the TLS certificate

```
./scripts/init_letsencrypt.sh
```

One-time only. This does the standard nginx+certbot bootstrap dance
(temporary self-signed cert → real cert → reload) — see the script's
comments for why that dance is necessary. The `certbot` service in
`docker-compose.production.yml` then keeps the certificate renewed
automatically (checks twice daily, renews when due).

## 5. Launch

```
docker compose -f docker-compose.yml -f docker-compose.production.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.production.yml exec backend alembic upgrade head
docker compose -f docker-compose.yml -f docker-compose.production.yml exec backend python -m app.db.seed
```

Then verify:

```
./scripts/health_check.sh
```

## 6. Ongoing deploys

```
./scripts/deploy.sh
```

Pulls latest `main`, rebuilds images, restarts services, runs migrations,
re-seeds (idempotent), prunes old images, and runs the health check.

## 7. Backups

```
./scripts/backup_db.sh
```

Logical `pg_dump` backup, gzipped, to `./backups/`, with old backups beyond
`RETENTION_DAYS` (default 14) pruned automatically. Suggested cron (not
installed automatically):

```
0 3 * * * cd /path/to/AI-Engineering-OS && ./scripts/backup_db.sh >> /var/log/aeos_backup.log 2>&1
```

To restore:

```
./scripts/restore_db.sh backups/aeos_db_20260101_030000.sql.gz
```

**Why logical backups, not volume snapshots:** `pg_dump` output is
portable, human-inspectable, and restorable into any compatible Postgres
instance — simpler and more transparent than raw volume snapshotting for a
single-VPS MVP. If the VPS provider offers disk snapshots, those are a
reasonable *additional* safety net, not a replacement.

## 8. Monitoring & logging (lightweight, MVP-appropriate)

No Prometheus/Grafana/ELK stack is stood up here — that's real
infrastructure overhead for a 10-student pilot on a single VPS, and
contradicts "avoid overengineering." Instead:

- Every service already emits structured JSON logs (Coding Standards) and
  `docker-compose.production.yml` caps them at 10MB × 3 files per service
  (`json-file` driver), so logs can't silently fill the disk.
- Docker-native `healthcheck:` blocks are defined for frontend, backend,
  postgres, and redis — Docker will report unhealthy containers via
  `docker ps` / `docker compose ps`, and can be configured to auto-restart.
- `scripts/health_check.sh` gives a one-command status check; point an
  external uptime monitor (e.g. UptimeRobot, free tier) at
  `https://$DOMAIN/api/v1/health` for alerting without running anything
  extra yourself.
- View live logs with `docker compose -f docker-compose.yml -f
  docker-compose.production.yml logs -f [service]`.

**Future Scale Path** (per `02_ARCHITECTURE.md`'s own section): if the
platform grows well beyond the pilot, add Prometheus + Grafana (or a
hosted equivalent) and centralized log shipping then — not before.

## 9. CI/CD

`.github/workflows/ci.yml` runs on every push/PR to `main`:
lint + test (backend, executor), build (frontend). The `deploy` job is
gated to **manual dispatch** (Actions tab → "Run workflow"), not automatic
on every push — a human confirms each production rollout during the pilot.

Required repository secrets for the deploy job: `VPS_HOST`, `VPS_USER`,
`VPS_SSH_KEY`, `VPS_APP_DIR`.

## 10. Security hardening summary

- UFW: only 22 (SSH), 80, 443 open.
- fail2ban: SSH brute-force protection.
- Nginx: HTTPS-only (HTTP redirects to HTTPS), security headers
  (`X-Frame-Options`, `X-Content-Type-Options`, `Strict-Transport-Security`,
  `Referrer-Policy`), and `limit_req` rate limiting as defense-in-depth on
  top of (not instead of) the Authentication Module's own app-level login
  rate limiting.
- `docker-compose.production.yml` removes host port publishing for
  postgres/redis/backend — only nginx is internet-reachable; everything
  else is internal-Docker-network-only.
- Backend and frontend containers run as non-root users (see
  `apps/backend/Dockerfile` / `apps/frontend/Dockerfile`). **The executor
  container still runs as root** — it needs `/var/run/docker.sock` access
  to launch sandbox containers, and matching a non-root user's GID to the
  host's docker group reliably across environments was judged not worth
  the fragility for this MVP. This is a known, documented trade-off (see
  Known Issues in `context/project_state.md`), not an oversight.
- All secrets (`JWT_SECRET`, `JWT_REFRESH_SECRET`, `INTERNAL_SERVICE_TOKEN`,
  `POSTGRES_PASSWORD`) must be regenerated for production — the checked-in
  `.env.production.example` only has placeholders that fail obviously if
  left unchanged.

## Known limitations of this deployment design

See `context/project_state.md`'s Known Issues for the full list — in
short: single VPS (no redundancy/failover), executor runs as root (DooD +
docker.sock), no automated rollback on failed deploys, and no log
aggregation beyond local Docker logs. All reasonable trade-offs for a
10-student pilot; revisit before scaling further.
