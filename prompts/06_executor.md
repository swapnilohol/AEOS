# CODE EXECUTION ENGINE MODULE

Note: like prompts/05_editor.md, this uploaded file's own text says
"Generate only Executor Module implementation prompt... Do not generate
code." Per explicit user instruction in the conversation, this module
implements the real Docker-based execution engine instead.

Load:

00_MASTER_CONTEXT.md
01_GLOBAL_RULES.md
02_ARCHITECTURE.md
03_CODING_STANDARDS.md
prompts/01_database.md
prompts/02_auth.md
prompts/03_admin.md (Student Management)
prompts/03b_admin_module.md (Admin: Problem Management + Analytics)
prompts/05_editor.md
context/project_state.md

Objective:

Execute student-submitted code securely (Docker sandbox, no network access,
CPU/memory/timeout limits) for Python 3.12, Java 21, C++17, and Node.js.
Store per-test execution_results and a weighted score per submission.

Architecture:

Submission API (Editor Module) -> Redis queue -> Executor worker ->
Docker sandbox -> Result Processor -> Database

Do not regenerate Bootstrap, Database, Authentication, Student Management,
Admin, or Editor modules. Integration edits only where required:
- app/core/queue.py (new) + one enqueue call in editor_service.py
- docker-compose.yml executor service (docker.sock mount, depends_on fix)

API:

GET /api/v1/submissions                  (own, optional problem_id filter)
GET /api/v1/submissions/{id}
GET /api/v1/submissions/{id}/results      (hidden-test details redacted for non-admin)

Repository Version:
0.7.0

Next Prompt:
prompts/07_scoring.md
