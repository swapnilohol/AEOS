# DASHBOARD MODULE

Note: like prompts/05_editor.md, 06_executor.md, and 07_scoring.md, this
uploaded file's own text says "Generate only Dashboard Module implementation
prompt... Do not generate code." Per explicit user instruction, the real
implementation (backend + frontend) was built instead.

Load: 00_MASTER_CONTEXT.md, 01_GLOBAL_RULES.md, 02_ARCHITECTURE.md,
03_CODING_STANDARDS.md, prompts/01_database.md, prompts/02_auth.md,
prompts/03_admin.md, prompts/03b_admin_module.md, prompts/05_editor.md,
prompts/06_executor.md, prompts/07_scoring.md, context/project_state.md

Objective: role-based dashboards (Admin, Student) composing existing
Admin/Scoring/Student data, plus activity tracking and structured reports.

Architecture: Dashboard Controller -> Dashboard Service -> Analytics
Service -> Repository Layer -> Database (composition over duplication;
Analytics/Report services reuse AdminRepository/ScoringRepository/
StudentRepository rather than re-querying).

Database:
- activity_logs (new: id, user_id, activity_type, metadata_json [renamed
  from `metadata`, which collides with SQLAlchemy's Base.metadata],
  created_at)
- dashboard_statistics cache table: intentionally NOT created (see
  docs/README.md) — prompt marks it optional, and on-demand queries are
  fast enough at 10-student scale.

API:
GET /api/v1/dashboard/admin/overview
GET /api/v1/dashboard/admin/analytics
GET /api/v1/dashboard/admin/activity
GET /api/v1/dashboard/admin/reports/student/{user_id}
GET /api/v1/dashboard/admin/reports/submissions
GET /api/v1/dashboard/admin/reports/hackathon-summary
GET /api/v1/dashboard/student/overview
GET /api/v1/dashboard/student/performance
GET /api/v1/dashboard/student/leaderboard

Do not regenerate Bootstrap, Database, Authentication, Student Management,
Admin, Editor, Execution Engine, or Scoring modules. Integration edits only:
one activity-log call each in auth_service.login, editor_service
.submit_solution, scoring_service.calculate_for_submission.

Frontend: new pages only (/admin/analytics, /admin/reports,
/student/dashboard, /student/performance, /student/leaderboard) — existing
/admin and /student pages left untouched.

Repository Version:
1.0.0

Next Prompt:
prompts/09_deployment.md
