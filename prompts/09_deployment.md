# DEPLOYMENT MODULE

Note: like the four modules before it, this uploaded file's own text says
"Generate only Deployment Module implementation prompt... Do not generate
code." Per explicit user instruction, the real deployment configuration
was built. This module is almost entirely infra/ops config rather than
application code, so "do not modify business logic" was never in tension
with it.

Load: 00_MASTER_CONTEXT.md, 01_GLOBAL_RULES.md, 02_ARCHITECTURE.md,
03_CODING_STANDARDS.md, prompts/01_database.md through prompts/08_dashboard.md,
context/project_state.md

Objective: production deployment architecture for a single Ubuntu VPS —
Docker Compose (no Kubernetes), Nginx + Let's Encrypt HTTPS, environment
management, deployment/backup scripts, lightweight monitoring, CI/CD.

Generated (all new except two justified, documented hardening edits):
- docker-compose.production.yml (overlay, not a rewrite of docker-compose.yml)
- infrastructure/nginx/production.conf.template (envsubst-based, ${DOMAIN})
- .env.production.example
- scripts/{setup_vps,init_letsencrypt,deploy,health_check,backup_db,restore_db}.sh
- .github/workflows/ci.yml (lint/test/build on push; manual-dispatch deploy)
- docs/deployment.md (full runbook)

Two small edits to prior-module files (documented in docs/README.md):
- docker-compose.yml: nginx volume mount changed from directory to
  specific file (mechanical, same dev behavior, avoids prod-overlay collision)
- apps/backend/Dockerfile, apps/frontend/Dockerfile: added non-root USER
  (apps/executor/Dockerfile deliberately left as root — needs
  /var/run/docker.sock; documented trade-off)

Do not regenerate previous modules. Do not modify business logic.

Repository Version:
1.1.0

Next Prompt:
None — all planned AEOS modules are complete. Future work (monitoring
stack, multi-college support, etc.) would need a new prompt file.
