# SCORING MODULE

Note: like prompts/05_editor.md and 06_executor.md, this uploaded file's
own text says "Generate only Scoring Module implementation prompt... Do not
generate code." Its "Final Score Formula" section is also cut off
mid-sentence in the source file. Per explicit user instruction, the real
implementation was built, with the formula designed by this module (see
docs/README.md) to fill the gap left by the truncated spec.

Load:

00_MASTER_CONTEXT.md, 01_GLOBAL_RULES.md, 02_ARCHITECTURE.md,
03_CODING_STANDARDS.md, prompts/01_database.md, prompts/02_auth.md,
prompts/03_admin.md, prompts/03b_admin_module.md, prompts/05_editor.md,
prompts/06_executor.md, context/project_state.md

Objective:

Convert Execution Engine results into final, weighted, penalized scores;
maintain a leaderboard; expose score history and breakdown APIs.

Architecture:

Execution Results -> Score Service -> Score Records -> Leaderboard Service
-> Dashboard Analytics (backend-only; Controller -> Service -> Calculation
Engine -> Repository -> Database)

Database:

problems.difficulty_multiplier (new column, default 1.0)
score_breakdowns (new table: score_id unique FK, functional_score,
performance_factor, difficulty_multiplier, penalty_factor, quality_score
nullable, final_score)

API:

POST /api/v1/internal/scoring/submissions/{id}/calculate  (internal token, called by executor)
GET  /api/v1/scoring/submissions/{id}/breakdown            (owner/ADMIN)
GET  /api/v1/scoring/history                               (own; ADMIN can pass user_id)
GET  /api/v1/scoring/leaderboard/{hackathon_id}             (any authenticated user)

Do not regenerate Bootstrap, Database, Authentication, Student Management,
Admin, Editor, or Execution Engine modules. Integration edits only:
Problem model (+1 column), executor processor.py (+1 trigger call).

No UI implementation in this module.

Repository Version:
0.8.0

Next Prompt:
prompts/08_dashboard.md
