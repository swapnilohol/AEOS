# EDITOR MODULE

Note: the uploaded prompt file's own text says "Generate only Editor Module
implementation prompt... Do not generate code" (i.e., read literally, a
design-only step). Per explicit user instruction in the conversation, this
module implements the real thing instead: database tables, APIs, and
frontend pages/components for the student coding workspace.

Load:

00_MASTER_CONTEXT.md
01_GLOBAL_RULES.md
02_ARCHITECTURE.md
03_CODING_STANDARDS.md
prompts/01_database.md
prompts/02_auth.md
prompts/03_admin.md (Student Management)
prompts/03b_admin_module.md (Admin: Problem Management + Analytics)
context/project_state.md

Objective:

Editor workspace where students solve assigned problems.

Features:
- Code Editor Interface (Monaco)
- Problem Workspace
- Language Selection
- Draft Management (autosave)
- Solution Submission Preparation
- Editor Dashboard
- Role Based Access
- Secure Coding Workflow

Database:

code_drafts (id, user_id, problem_id, language, code, created_at,
updated_at; unique on user_id+problem_id)

editor_sessions (id, user_id, problem_id, language, status, started_at,
last_active_at, ended_at, created_at, updated_at)

"EDITOR_SESSION" from the prompt is implemented as this table/entity, not
as a roles-table RBAC role (see docs/README.md).

API:

PUT/GET   /api/v1/editor/problems/{id}/draft
POST      /api/v1/editor/problems/{id}/sessions
PATCH     /api/v1/editor/sessions/{id}/heartbeat
POST      /api/v1/editor/sessions/{id}/end
GET       /api/v1/editor/sessions/active            (ADMIN)
POST      /api/v1/editor/problems/{id}/submit
GET       /api/v1/editor/problems/{id}/workspace

Do not modify Bootstrap, Database, Authentication, Admin, or Student
Management modules.

Repository Version:
0.6.0

Next Prompt:
Execution Engine (to consume PENDING submissions created here) or the
fuller Student Portal UI.
