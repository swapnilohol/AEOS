# AI Elite Internship Hackathon Platform

TheGCPal Labs — AI Engineering Operating System (AEOS)

Live AI internship hackathon platform. Evaluates students through real
engineering problems, executed and scored automatically, instead of MCQs.

Pilot: Newton Institute of Science and Technology
Target: 10 concurrent students

## Stack

- Frontend: Next.js 15, TypeScript, TailwindCSS, Monaco Editor
- Backend: FastAPI, Python 3.12
- Database: PostgreSQL
- Cache: Redis
- Execution: Docker Sandbox
- Deployment: Docker Compose, Nginx, HTTPS

## Repository Structure

```
apps/
  frontend/   Next.js student + admin portal
  backend/    FastAPI modular monolith
  executor/   Docker sandbox execution service
packages/
  shared/     Shared types/utilities
docs/         Documentation
scripts/      Operational scripts
infrastructure/ Nginx + deployment config
context/      AEOS context + repository state
prompts/      AEOS module prompts
```

## Getting Started

1. Copy environment file:
   ```
   cp .env.example .env
   ```
2. Start all services:
   ```
   docker compose up --build
   ```
3. Frontend: http://localhost:3000
4. Backend health check: http://localhost:8000/health

## Database

PostgreSQL schema is managed with SQLAlchemy 2.x models + Alembic migrations
under `apps/backend`.

Entities: `roles`, `users`, `hackathons`, `problems`, `problem_tests`,
`submissions`, `execution_results`, `scores`, `violations`,
`leaderboard_entries`.

Apply migrations and seed baseline data (roles, pilot hackathon, 4 problems)
after `docker compose up`:

```
./scripts/migrate_and_seed.sh
```

## Authentication

JWT-based auth with access + refresh tokens (httpOnly cookies), bcrypt
password hashing, RBAC (`ADMIN` / `STUDENT`), account lockout after repeated
failed logins, and per-IP rate limiting on `/auth/login` and `/auth/refresh`.

API base: `/api/v1/auth`

- `POST /login` — authenticate, sets `access_token` + `refresh_token` cookies
- `POST /refresh` — rotates tokens using the refresh cookie
- `POST /logout` — revokes the refresh session
- `GET /me` — current authenticated user
- `POST /change-password` — update password (revokes other sessions)
- `POST /admin/create-student` — ADMIN only, creates a student account

Frontend: `/login` (student), `/admin/login` (admin). `middleware.ts`
redirects unauthenticated requests away from `/admin/*` and `/student/*`.

## Student Management

Admin-managed student accounts + self-service profile, built on top of
Authentication (unmodified). API base: `/api/v1/students`.

Admin (ADMIN role required):
- `POST /students` — create a student (account + profile in one call)
- `GET /students` — list/search students (paginated)
- `GET /students/{id}` — student details
- `PUT /students/{id}` — update a student
- `DELETE /students/{id}` — remove a student

Student (own data only):
- `GET /students/me` — own profile
- `PUT /students/me` — update own profile (restricted fields)
- `GET /students/dashboard` — own submission/score summary

## Admin Module (Problem Management + Analytics)

**Problem Management** — `/api/v1/problems`:
- `POST /problems`, `PUT /problems/{id}`, `DELETE /problems/{id}` — ADMIN only
- `GET /problems`, `GET /problems/{id}` — any authenticated user

- `POST/GET/PUT/DELETE /problems/{id}/tests` — ADMIN only end-to-end (hidden
  test expected outputs are never exposed to students)

**Admin Analytics** — `GET /api/v1/admin/dashboard` (ADMIN only): student/
problem/submission/violation counts, active hackathon summary, submission
status breakdown, top scores.

**Admin Frontend** — `/admin` (dashboard), `/admin/students` (search/list),
`/admin/problems` (list + create), all behind the existing cookie-based
`middleware.ts` redirect.

## Editor Module

Student coding workspace built on Monaco. API base: `/api/v1/editor`.

- `PUT/GET /editor/problems/{id}/draft` — autosaved draft (STUDENT, own only)
- `POST /editor/problems/{id}/sessions` — start/resume a workspace session
- `PATCH /editor/sessions/{id}/heartbeat`, `POST /editor/sessions/{id}/end`
- `GET /editor/sessions/active` — ADMIN monitoring of live sessions
- `POST /editor/problems/{id}/submit` — creates a `PENDING` submission from
  the draft (or explicit code); running it against tests is the Execution
  Engine module's job, not this one
- `GET /editor/problems/{id}/workspace` — aggregate view (problem, draft,
  session, remaining time, submission status) powering the dashboard

Frontend: `/student` (problem list) → `/student/problems/{id}` (editor
workspace: problem header, Monaco panel, save/submit/full-screen toolbar,
submission status).

## Execution Engine

Submissions created by the Editor Module are pushed onto a Redis queue and
processed by the `executor` service: each one runs in an isolated,
ephemeral Docker container with **no network access**, a CPU limit, a
memory limit, and an execution timeout (all from `.env`:
`EXECUTOR_CPU_LIMIT`, `EXECUTOR_MEMORY_LIMIT`, `EXECUTOR_TIMEOUT_SECONDS`).

Supported languages: Python 3.12, Java 21, C++17 (g++), Node.js
(JavaScript). Each submission runs against every one of its problem's test
cases (public and hidden); results are stored in `execution_results` and a
weighted score in `scores`.

API base: `/api/v1/submissions` (read-only status/results, owner or ADMIN;
hidden-test details are redacted for non-admin viewers).

**Security note:** the executor needs Docker socket access to launch sibling
containers ("Docker outside of Docker"), which is a known trust trade-off —
see `docs/README.md` for details and hardening options.

## Scoring Module

Builds a refined final score on top of the Execution Engine's raw
functional score. Triggered automatically: the executor calls an internal
backend endpoint right after a submission completes.

`final_score = functional_score * performance_factor * penalty_factor`,
always within `[0, problem.max_score]`. `performance_factor` softly
penalizes slow execution (bounded); `penalty_factor` applies a late-submission
deduction. `difficulty_multiplier` scales a problem's contribution to a
student's **leaderboard total**, not the per-submission score. Full formula
and rationale in `docs/README.md` (the source prompt's own formula section
was cut off — this module documents the gap-filling design explicitly).

API base: `/api/v1/scoring` (+ `/api/v1/internal/scoring` for the
executor's service-to-service callback):
- `GET /scoring/submissions/{id}/breakdown` — owner or ADMIN
- `GET /scoring/history` — own score history (ADMIN can pass `user_id`)
- `GET /scoring/leaderboard/{hackathon_id}` — any authenticated user
- `POST /internal/scoring/submissions/{id}/calculate` — internal token auth
  only (called by the executor, not user-facing)

## Dashboard Module

Role-based dashboards built on top of Admin/Scoring/Student data — no new
scoring or execution logic, just aggregation and presentation.

**Admin** (`/api/v1/dashboard/admin/*`, ADMIN only):
- `GET /overview` — platform stats + live status + active hackathon
- `GET /analytics` — problem completion rate, score distribution, execution stats
- `GET /activity` — recent activity feed (login, submission, score events)
- `GET /reports/student/{user_id}`, `/reports/submissions`, `/reports/hackathon-summary`
  — structured JSON reports (no PDF/CSV export in this MVP)

**Student** (`/api/v1/dashboard/student/*`, STUDENT only, own data only):
- `GET /overview` — profile, assessment status, progress, rank
- `GET /performance` — score history for charting
- `GET /leaderboard` — own rank + public top 10

Frontend: `/admin/analytics`, `/admin/reports` (new); `/student/dashboard`,
`/student/performance`, `/student/leaderboard` (new). Existing pages from
prior modules (`/admin`, `/student`) were left untouched. Polling-based
(no WebSocket) — sufficient for 10 concurrent students.

## Deployment

Single Ubuntu VPS, Docker Compose (no Kubernetes/managed platform). Full
runbook: [`docs/deployment.md`](docs/deployment.md).

```
./scripts/setup_vps.sh          # one-time server bootstrap
cp .env.production.example .env # fill in real secrets/domain
./scripts/init_letsencrypt.sh   # one-time TLS certificate issuance
./scripts/deploy.sh             # build, migrate, launch (and every deploy after)
```

Production overlay: `docker-compose.production.yml` (used via
`-f docker-compose.yml -f docker-compose.production.yml`) — HTTPS via
Nginx + Let's Encrypt (auto-renewing), internal-network-only postgres/
redis/backend, resource limits, log rotation, healthchecks. Backups via
`./scripts/backup_db.sh` / `./scripts/restore_db.sh`. CI/CD via
`.github/workflows/ci.yml` (lint/test/build on every push; manual-dispatch
deploy).

## Status

Bootstrap, Database, Authentication, Student Management, Admin Module,
Editor Module, Execution Engine, Scoring Module, Dashboard Module,
Deployment Module, and the Final System Review are all complete.

**Launch decision:** REQUIRES FIRST LIVE RUN — see
[`docs/final_review.md`](docs/final_review.md) for the full audit. No
code-level blocking defects were found; the repository has simply never
been run against a real Postgres/Redis/Docker stack (this environment has
no network access). Becomes production-ready for the 10-student pilot once
one successful live end-to-end run is confirmed.

See `context/project_state.md` for current repository state and the full
technical debt list.

## Engineering Rules

This repository follows the AEOS Global Rules and Coding Standards.
One module is implemented at a time. See `prompts/` for the module sequence.
## Current Implementation Status

### Implemented Features

#### Authentication

* JWT Login Authentication
* Role Based Access Control (ADMIN / STUDENT)

#### Student Features

* Dashboard
* Problems List
* Problem Details Page
* Code Submission
* Submission History
* Leaderboard

#### Admin Features

* Admin Dashboard
* Problem Creation
* Test Case Creation
* Submission Monitoring

#### Code Execution

* Python Code Execution Engine
* Automatic Test Case Evaluation
* ACCEPTED / WRONG_ANSWER Status
* Automatic Score Calculation

### Current Database Tables

* users
* problems
* test_cases
* submissions

### Running Services

Frontend:

```text id="fe"
http://localhost:3000
```

Backend:

```text id="be"
http://127.0.0.1:8000
```

Swagger API Docs:

```text id="sw"
http://127.0.0.1:8000/docs
```

### Current Leaderboard State

```text id="lb"
Rank #1 : swapnil
Solved Problems : 4
Score : 400
```

### Future Enhancements

* Java Executor
* C++ Executor
* Docker Sandbox Isolation
* Contest Mode
* Real-time Analytics
* Production Deployment
