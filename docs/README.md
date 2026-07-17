# Documentation

Module-level documentation is added here as each AEOS module is completed
(API docs, environment docs, architecture notes).

## Database Module (0.2.0)

Schema: `roles`, `users`, `hackathons`, `problems`, `problem_tests`,
`submissions`, `execution_results`, `scores`, `violations`,
`leaderboard_entries`. All tables use UUID primary keys and
`created_at`/`updated_at` timestamps.

Migration tool: Alembic (`apps/backend/alembic/`). Initial migration:
`0001_initial_schema.py`.

Seed data: roles `ADMIN`/`STUDENT`, one pilot hackathon, and its 4 problems
(Semantic Resume Intelligence, Multi-Agent Interview Scheduler, AI Fraud
Detection Engine, Decision Intelligence Agent). Run via
`app/db/seed.py` or `scripts/migrate_and_seed.sh`.

No APIs were generated in this module.

## Authentication Module (0.3.0)

**Users table changes** (migration `0002_add_auth_fields_to_users`): added
`username` (nullable, unique), `last_login_at`, `refresh_token_hash`,
`failed_login_attempts`, `locked_until`. Role stays a normalized FK
(`role_id` → `roles.id`, exposed via `User.role` relationship) rather than a
duplicated string column, per the no-duplicated-data rule; the API always
returns the resolved role name.

**Tokens:** HS256 JWTs. Access token 30 min (separate `JWT_SECRET`), refresh
token 7 days (separate `JWT_REFRESH_SECRET`), rotated on every `/refresh`
call. Refresh tokens are stored server-side only as a SHA-256 hash.

**Cookies:** `access_token` and `refresh_token` are set as `httpOnly`,
`SameSite=Lax` cookies (`Secure` when `COOKIE_SECURE=true`). The API also
accepts a `Authorization: Bearer <token>` header as an alternative.

**Account protection:** after `LOGIN_MAX_ATTEMPTS` (default 5) consecutive
failed logins, the account is locked for `LOGIN_LOCKOUT_MINUTES` (default
15). Login/refresh are additionally rate-limited per IP via Redis (10
requests/minute) — see `app/middlewares/auth_middleware.py`.

**RBAC:** `app/dependencies/auth.py` provides `get_current_user` and
`require_roles(*roles)`. `/admin/create-student` requires `ADMIN`.

**Error format:** all expected auth failures (invalid credentials, locked
account, expired token, forbidden role, validation errors) are normalized to
the standard `{success, message, data, errors}` shape via
`app/middlewares/http_exception_handler.py`, registered alongside the
existing unhandled-exception handler from Bootstrap.

**Deviation from prompt file paths:** the prompt requested a top-level
`middleware/` folder; this was consolidated into the existing `middlewares/`
package created in Bootstrap to avoid duplicate parallel folders (Global
Rules: never duplicate modules).

## Student Management Module (0.4.0)

**Database:** new `student_profiles` table (migration
`0003_create_student_profiles`), linked to `users` via a unique `user_id`
FK — implemented as effectively 1:1 rather than the prompt's stated "1:Many"
relationship, since the prompt's own constraint (`user_id UNIQUE`) only
supports one profile per user. `student_id` is separately unique.

**Layering:** `api/v1/students.py` (controller) → `services/student_service.py`
(business logic) → `repositories/student_repository.py` (DB only), matching
the same Clean Architecture pattern as Authentication.

**Reuses, does not modify, Authentication:** `StudentService.create_student`
calls the existing `AuthService.create_student` to create the underlying
`User` row, then attaches a `StudentProfile`. Because `AuthService.create_student`
commits independently, cross-table atomicity isn't available without
touching the Auth module (out of scope here). If profile creation
subsequently fails (e.g. duplicate `student_id`), the service compensates by
deactivating the orphaned `User` row rather than leaving a broken,
profile-less account silently active. This is a known trade-off — see
Known Issues.

**Naming deviation:** the prompt asked for `StudentService` /
`StudentServiceImpl` (interface + implementation) and exception classes
suffixed `Exception`. This codebase uses a single `StudentService` class
(no interface split) and `Error`-suffixed exceptions
(`StudentNotFoundError`, `DuplicateStudentError`), consistent with the
Python/FastAPI conventions already established in the Authentication
module and with the Global Rule to avoid unnecessary abstractions.

**Validation:** password complexity (upper/lower/digit/special, 8+ chars),
semester restricted to 1–8, phone numbers checked against a simple E.164-ish
pattern — all enforced in `schemas/student.py`, not in the Auth module.

**RBAC:** all `/students` routes except `/me` and `/dashboard` require
`ADMIN` via the existing `require_roles` dependency from the Auth module.

No Admin Dashboard UI, Problem Management, or Analytics were generated in
this module — they were not specified in this prompt.

## Admin Module: Problem Management + Analytics (0.5.0)

**Naming note:** the source prompt file `prompts/03_admin.md` is titled
"Student Management Module" and its body only specifies student CRUD (which
was built in the 0.4.0 module above). Per explicit instruction, this module
follows the *filename* ("Admin") rather than that mismatched body, and adds
what a Student Management module's prompt did not: Problem Management,
Admin Analytics, and Admin-facing frontend pages — without modifying
Bootstrap, Database, Authentication, or the existing Student Management
files.

**Problem Management:** `schemas/problem.py`, `repositories/problem_repository.py`,
`services/problem_service.py`, `api/v1/problems.py`. Same Clean Architecture
layering as Students. No changes to the `Problem` / `ProblemTest` models —
they already existed from the Database module.

**Read/write split:** problem listing and detail (`GET /problems`,
`GET /problems/{id}`) are open to any authenticated user (students will need
this once the Student Portal exists), while creation/update/deletion and
**all** problem-test endpoints are ADMIN-only. Test cases are gated
end-to-end (not just hidden ones) because exposing `expected_output` for
*any* test case before the Execution Engine module exists would let a
student read grading answers directly.

**Admin Analytics:** `schemas/admin.py`, `repositories/admin_repository.py`
(read-only aggregate queries), `services/admin_service.py`,
`api/v1/admin.py` → `GET /admin/dashboard` (ADMIN only). Aggregates: student
count (via `Role`/`User`), problem count, submission count, violation count,
the currently active `Hackathon` (if any) with its problem count, a
submission status breakdown, and a top-5 score leaderboard preview (sum of
`Score.points` per user) — all read-only queries against existing Database
module tables.

**Admin Frontend:** `/admin` (dashboard cards + status breakdown + top
scores), `/admin/students` (search/list, calls the existing `/students`
API), `/admin/problems` (list + create form, calls the new `/problems`
API). All three are already protected by the `middleware.ts` cookie check
from the Authentication module (`matcher: ["/admin/:path*", ...]`) — no
middleware changes were needed.

No Monaco Editor, Execution Engine, Evaluation Engine, or Leaderboard were
generated in this module.

## Editor Module (0.6.0)

**Scope note:** the source file `prompts/05_editor.md` explicitly states
"Generate only Editor Module implementation prompt... Do not generate
code" — read literally, it asks for a design document, not an
implementation. Per explicit user instruction in the conversation, this
module implements the real thing (tables, APIs, frontend) rather than a
prompt-about-a-prompt, since that was the direct, current-turn request.

**Database:** two new tables (migration `0004_create_editor_tables`):
`code_drafts` (one row per student+problem, unique constraint, upserted on
every save) and `editor_sessions` (workspace lifecycle: `ACTIVE`/`ENDED`,
`started_at`/`last_active_at`/`ended_at`).

**"EDITOR_SESSION" interpretation:** the prompt lists `EDITOR_SESSION`
alongside `ADMIN`/`STUDENT` under "Editor Role Management," describing it as
"a temporary coding workspace." This is a resource/session concept, not an
authentication identity — adding it to the `roles` table would break RBAC
semantics for no benefit and would require touching the Authentication
module (out of scope, and explicitly not to be modified). It's implemented
as the `editor_sessions` table/entity instead; `ADMIN` and `STUDENT` remain
the only real RBAC roles.

**Layering:** `api/v1/editor.py` → `services/editor_service.py` →
`repositories/editor_repository.py`, reusing (not modifying)
`ProblemRepository` for problem lookups and `AdminRepository` for the active
hackathon's end time (remaining-time countdown).

**Submission preparation boundary:** `POST /editor/problems/{id}/submit`
creates a `Submission` row with `status=PENDING` using the student's draft
(or explicit code) — it does not run code against test cases. Executing
submissions and populating `execution_results`/`scores` remains the
Execution Engine module's responsibility, consistent with the Architecture
doc's `Student Submit → Backend API → Executor Service` flow.

**Test-case confidentiality carried over:** as in the Admin Module, problem
test cases stay ADMIN-only; the Editor Module never exposes
`expected_output` to students.

**Frontend:** `components/CodeEditorPanel.tsx` wraps `@monaco-editor/react`
(dynamically imported, `ssr: false`) with language selection and a
full-screen toggle. `/student/problems/{id}` assembles the Problem Header,
Editor Panel, Action Toolbar (Save/Submit/Full Screen), and Submission
Status Panel per the prompt's layout, with autosave (debounced) and a
periodic session heartbeat. `/student` is a minimal problem list added only
so the workspace is reachable — the fuller Student Portal (profile,
submission history UI) remains a separate future module.

**Dependency added:** `@monaco-editor/react` in `apps/frontend/package.json`.

## Execution Engine (0.7.0)

**Scope note:** like `prompts/05_editor.md`, the uploaded
`prompts/06_executor.md` says "Generate only Executor Module implementation
prompt... Do not generate code." Per explicit user instruction, this module
implements the real thing, consistent with how the Editor Module's identical
conflict was resolved.

**Architecture:** `Submission API (Editor Module) → Redis queue →
Executor worker → Docker sandbox → Result Processor → Database`, matching
the Architecture doc's Execution Flow exactly.

**Queue:** `app/core/queue.py` (backend) pushes a submission ID onto a Redis
list (`execution_queue`) after `EditorService.submit_solution` commits — the
only integration edit made to the Editor Module, justified by "modify
previous files only if integration is required." The executor's
`runner/queue_client.py` blocks on `BRPOP` with a timeout so the worker loop
can check for shutdown signals.

**Multi-language support:** `images/language_configs.py` maps each of
Python 3.12, Java 21, C++17, and Node.js to a Docker image and
compile/run command:

| Language   | Image                  | Compile             | Run                  |
|------------|------------------------|----------------------|----------------------|
| python     | python:3.12-slim       | —                    | `python3 main.py`    |
| javascript | node:22-alpine         | —                    | `node main.js`       |
| java       | eclipse-temurin:21-jdk | `javac Main.java`    | `java Main`          |
| cpp        | gcc:13                 | `g++ -std=c++17 ...` | `./main`             |

Java submissions must define `public class Main`. Test input is piped via
stdin redirection (`< input.txt`), so this works uniformly across compiled
and interpreted languages.

**Sandbox isolation** (`sandbox/docker_runner.py`): each run is an ephemeral
container (`remove=True`-equivalent via explicit `container.remove(force=True)`
in a `finally` block) with `network_mode="none"` (no network access, per the
Global Rule), a memory limit (`mem_limit`), a CPU limit (`nano_cpus`), a
non-root user (`1000:1000`), and a wall-clock timeout enforced via
`container.wait(timeout=...)` — on timeout the container is killed and the
result is marked `timed_out`.

**Result processing** (`runner/processor.py`): marks the submission
`RUNNING`, runs every `ProblemTest` for the problem (public and hidden
alike — the executor doesn't discriminate, since it needs the real
expected output to grade), stores one `ExecutionResult` per test
(`passed`, `actual_output` truncated to 5000 chars, `execution_time_ms`,
`error_message` truncated to 2000 chars), computes a weighted score via
`utils/scoring.py` (`sum(weight for passed tests) / sum(all weights) *
problem.max_score`), upserts one `Score` row, and marks the submission
`COMPLETED`. Any unhandled exception during processing marks it `FAILED`
instead, so a single bad submission can't wedge the worker loop or leave a
submission stuck `RUNNING` forever.

**Duplicated data layer (documented tech debt):** `apps/executor` is a
separate Docker build context from `apps/backend` (see `docker-compose.yml`),
so it cannot import `apps/backend/app/models`. `runner/db.py` mirrors just
the columns the executor reads/writes (`submissions`, `problems`,
`problem_tests`, `execution_results`, `scores`). Any future migration
touching those tables must be kept in sync with this file until a shared
`packages/shared` package removes the duplication — this aligns with the
Architecture doc's own "Future Scale Path."

**Docker-outside-of-Docker security trade-off:** `docker-compose.yml` mounts
`/var/run/docker.sock` into the `executor` container so it can launch
sibling sandbox containers. This gives the executor container effectively
host-level Docker control — a well-known DooD caveat. Acceptable for a
10-student pilot on a single trusted VPS; a production hardening pass
should consider a Docker socket proxy with a restricted API surface, or
rootless/sysbox-style isolation, before scaling beyond the pilot.

**Submission Status APIs** (`api/v1/submissions.py`, backend, read-only):
`GET /submissions` (own, optionally filtered by `problem_id`),
`GET /submissions/{id}`, `GET /submissions/{id}/results` — all owner-or-ADMIN,
with hidden-test `actual_output`/`error_message` redacted (set to `null`)
for non-admin viewers, consistent with the hidden-test confidentiality
policy established in the Admin and Editor modules.

No Evaluation Engine (beyond the weighted scoring already computed here) or
Leaderboard were generated in this module.

## Scoring Module (0.8.0)

**Scope note:** like the Editor and Execution Engine modules, the uploaded
`prompts/07_scoring.md` says "Generate only Scoring Module implementation
prompt... Do not generate code." Per explicit user instruction, the real
implementation was built. Additionally, **the uploaded file's own "Final
Score Formula" section is cut off mid-sentence** — there is no formula to
transcribe. The formula below is this module's own design, filling that
gap; it is not a rendering of missing source content.

**Final Score Formula** (`app/services/scoring_engine.py`, pure functions):

```
final_score = functional_score * performance_factor * penalty_factor
```

- `functional_score`: the Execution Engine's existing weighted pass-ratio
  (`Score.points`, already in `[0, max_score]`) — reused, not recomputed,
  to avoid duplicating that logic.
- `performance_factor` ∈ `[1 - PERFORMANCE_MAX_PENALTY_RATIO, 1.0]`: no
  penalty if the average execution time of *passed* tests is at or under
  `PERFORMANCE_TARGET_MS`; scales down linearly beyond that, capped at the
  configured max penalty (default 10%). A bounded heuristic, not a precise
  metric.
- `penalty_factor`: `1.0` normally, `(1 - LATE_PENALTY_RATIO)` (default 20%)
  if `submission.submitted_at` is after the problem's hackathon's
  `end_time`.
- `quality_score`: included in the schema as an optional field, always
  `null` in this MVP. Static code-quality analysis was judged out of scope
  (would need a linting/analysis engine per language) — better to leave it
  genuinely absent than fabricate a number.

Since both factors are ≤ 1.0 and `functional_score` ≤ `max_score`, the
product is defensively clamped but never actually needs to clamp upward.

**Difficulty weighting — deliberately NOT in the per-submission formula:**
`difficulty_multiplier` (new `problems.difficulty_multiplier` column,
default `1.0`) only scales a problem's contribution to a student's
**leaderboard total** (`app/services/leaderboard_engine.py`:
`compute_weighted_total` = sum of `best_final_score * difficulty_multiplier`
across a student's best submission per problem). Applying it directly to a
single submission's score risked pushing that submission above its own
problem's `max_score`, which would break the "always bounded to
`[0, max_score]`" invariant. Ranking (`rank_totals`) is a straightforward
descending sort with ties broken by user ID — a documented simplification,
not a tie-sensitive competition-grade ranking, appropriate for 10 students.

**Score History:** no new history table. Every submission already has its
own `Score` row (Database module) and now its own `ScoreBreakdown` row
(1:1 with `Score`), so a user's history for a problem is just those rows
ordered by time — reusing existing structure rather than duplicating it.

**Trigger mechanism:** rather than a second queue/worker (which would add
a background process Bootstrap never provisioned) or fully lazy compute-on-read,
the executor calls a new internal backend endpoint
(`POST /internal/scoring/submissions/{id}/calculate`) as the last step of
`processor.py`, right after committing the raw `Score`. This keeps
Controller → Service → Calculation Engine → Repository fully in the
backend (matching this prompt's architecture diagram, unlike the Execution
Engine which necessarily lives in the executor), while still making
scoring "automatically triggered" immediately after execution, per the
prompt's workflow diagram. The call is authenticated with a static shared
token (`X-Internal-Token` / `INTERNAL_SERVICE_TOKEN`), not a user JWT,
since the caller isn't a logged-in user — see `app/dependencies/internal.py`.
It is best-effort: a failed callback leaves the submission `COMPLETED` with
its raw functional score, recoverable by re-calling the same endpoint later
(no automatic retry is implemented — see Known Issues).

**Integration edits required** (per this module's explicit "modify only if
scoring integration is required" rule): added one column to the existing
`Problem` model (`difficulty_multiplier`), and one call
(`trigger_scoring(...)`) at the end of the executor's `processor.py`. No
other previous-module files were changed.

No Dashboard/Analytics UI or Leaderboard frontend were generated in this
module, per "No UI implementation yet unless required."

## Dashboard Module (1.0.0)

**Scope note:** like the three modules before it, `prompts/08_dashboard.md`
says "Generate only Dashboard Module implementation prompt... Do not
generate code." Per explicit user instruction, the real implementation
(backend + frontend) was built.

**Composition over duplication:** `AnalyticsService` and `ReportService`
compose the existing `AdminRepository` (Admin Module), `ScoringRepository`
(Scoring Module), and `StudentRepository` (Student Management Module)
rather than re-querying the same data. `DashboardRepository` holds only the
genuinely new queries this module needs (active-student count via open
`EditorSession`s, completion/timeout/distribution metrics, per-student
attempted/solved counts).

**`dashboard_statistics` cache table: intentionally NOT created.** The
prompt labels it "optional," and at 10 concurrent students the underlying
aggregate queries are trivially fast — adding a cache table would mean
cache-invalidation logic with no real benefit, contradicting the Global
Rule against premature optimization. All dashboard data is computed
on-demand. Revisit only if usage scales well beyond the pilot.

**`activity_logs` table:** new, append-only (no `updated_at`). The
prompt's field name `metadata` collides with SQLAlchemy's reserved
`Base.metadata` attribute, so the column is `metadata_json` (a string of
JSON) instead — a small, necessary, documented deviation.

**Activity Tracking — three minimal, justified integration edits** (per
this module's "modify previous modules only if dashboard integration is
required" rule):
- `auth_service.login()` logs `LOGIN` after a successful login.
- `editor_service.submit_solution()` logs `SUBMISSION_CREATED` after
  enqueueing (already modified once before, for the execution queue).
- `scoring_service.calculate_for_submission()` logs `SCORE_CALCULATED`
  after recomputing the leaderboard.

Execution-start/timeout events are **not** logged from the executor itself
— that would mean either a second cross-service HTTP call or duplicating
`activity_logs` into the executor's already-duplicated mirrored DB layer.
Both were judged higher cost than benefit for a "Recent Activity" feed
whose main value is showing login/submit/score events; noted as a Known
Issue rather than silently scoped out.

**Reports are plain JSON, not files:** per "avoid complex BI systems," the
three report endpoints return structured data for the frontend to render
(currently as raw JSON on `/admin/reports`). PDF/CSV export is a natural
future extension, not implemented here.

**Frontend — new pages only, existing pages untouched:** `/admin/analytics`,
`/admin/reports` (admin) and `/student/dashboard`, `/student/performance`,
`/student/leaderboard` (student) are new routes. The existing `/admin` and
`/student` pages from the Admin and Editor modules were left exactly as
they were — per "do not modify unchanged files," they do not yet link
forward to these new pages (see Known Issues). New shared components:
`StatsCard` (loading/error states, per the prompt's explicit requirement),
`components/dashboard/{AnalyticsChart,LeaderboardTable,ActivityFeed}.tsx`.
`AnalyticsChart` wraps `recharts` (bar/line only — no complex BI charting).

**Dependency added:** `recharts` in `apps/frontend/package.json`.

**Polling, not WebSocket:** all "live" data (active students, running
executions) is fetched on page load / manual refresh, matching the
prompt's explicit "MVP: Polling support acceptable." No polling interval
was wired into the pages themselves in this pass (see Known Issues) — the
APIs are polling-ready; auto-refresh is a small follow-up.

## Deployment Module (see docs/deployment.md for the full runbook)

**Scope note:** like the four modules before it, `prompts/09_deployment.md`
says "Generate only Deployment Module implementation prompt... Do not
generate code." Per explicit user instruction, the real deployment
configuration was built. This module is almost entirely infrastructure/ops
config rather than application code, so "do not modify business logic" was
never in tension with it.

**Two small, justified edits to prior-module files** (everything else is
net-new):
- `docker-compose.yml` (Bootstrap): nginx's volume mount changed from
  mounting the whole `infrastructure/nginx/` directory to mounting just
  `default.conf` by name. Purely mechanical — same effective content, same
  dev behavior — needed so the production overlay can add its own config
  to the same container without a path collision. Documented inline in the
  file itself.
- `apps/backend/Dockerfile` and `apps/frontend/Dockerfile` (Bootstrap):
  added a non-root `USER` directive to each, per this module's explicit
  "Security Hardening" deliverable. `apps/executor/Dockerfile` was
  deliberately left running as root — it needs `/var/run/docker.sock`
  access, and reliably matching a non-root user's GID to the host's docker
  group varies by environment; forcing it risked breaking sandbox
  execution for a hardening gain that's genuinely harder to get right here
  than for the other two services. Documented as a known trade-off, not an
  oversight.

**`docker-compose.production.yml`** (new, not a replacement): an overlay
applied via `-f docker-compose.yml -f docker-compose.production.yml`, not
a rewrite of the base file. Removes host port publishing for postgres/
redis/backend (nginx-only ingress), adds resource limits, log rotation,
and healthchecks, and adds the `certbot` renewal service.

**Nginx + Let's Encrypt:** `infrastructure/nginx/production.conf.template`
uses the official nginx image's built-in `envsubst`-on-templates mechanism
(mounted into `/etc/nginx/templates/`) to substitute `${DOMAIN}` at
container start — no custom sed/scripting needed. `scripts/init_letsencrypt.sh`
implements the standard temporary-self-signed-cert → real-cert → reload
bootstrap dance required because nginx needs certs to start, but certbot
needs nginx running to serve the ACME challenge.

**Monitoring:** deliberately lightweight — Docker-native healthchecks +
log rotation + a `health_check.sh` script + a pointer to an external free
uptime monitor, instead of standing up Prometheus/Grafana/ELK. Matches
"budget optimized deployment" and the Global Rule against overengineering;
full observability stack is filed under Architecture's own Future Scale
Path, not built now.

**Backups:** `pg_dump`-based logical backups (portable, inspectable),
gzipped, rotated, with a restore script — not raw volume snapshots.

**CI/CD:** `.github/workflows/ci.yml` lints/tests both Python services and
builds the frontend on every push/PR; the deploy job is gated to manual
`workflow_dispatch`, not automatic, so a human confirms each production
rollout during the pilot.

No business logic (any `app/services/*`, `app/api/*`, models, or frontend
page logic) was touched in this module.

## Final System Review (1.2.0)

Full pre-launch audit: [`docs/final_review.md`](final_review.md).
Produced by directly inspecting the repository (route-by-route auth
coverage, per-model index checks, layering-violation grep, secrets-hygiene
scan, file-size/TODO scan) rather than restating prior module summaries.
No new modules, no business-logic changes — review only, per this
module's own scope.

**Final decision:** REQUIRES FIRST LIVE RUN (not code defects — nothing in
this system, including migrations and Docker sandbox execution, has been
run outside this sandbox yet). Becomes READY FOR PRODUCTION for the
10-student pilot once one successful live end-to-end run is confirmed.
See the linked report for the full findings, technical debt list, and
launch checklist.
