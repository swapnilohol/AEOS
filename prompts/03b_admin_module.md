# ADMIN MODULE (Problem Management + Admin Analytics)

Note: the uploaded prompts/03_admin.md file is titled "Student Management
Module" and its body only covers student CRUD (already implemented in the
0.4.0 Student Management module). Per explicit user instruction, this
follow-up module follows the FILENAME ("Admin") rather than that mismatched
body, and implements what the filename implies but the body did not:

Generate:
- Admin Analytics / Dashboard API
- Problem Management APIs (Problem + ProblemTest CRUD)
- Admin Role Authorization (reuses existing require_roles from Auth module)
- Admin frontend pages (/admin, /admin/students, /admin/problems)

Do not regenerate:
- Bootstrap
- Database
- Authentication
- Student Management (0.4.0, already complete)

API:

/api/v1/problems                       POST/GET   (create: ADMIN, list: any user)
/api/v1/problems/{id}                   GET/PUT/DELETE (read: any user, write: ADMIN)
/api/v1/problems/{id}/tests             POST/GET   (ADMIN only)
/api/v1/problems/{id}/tests/{test_id}   PUT/DELETE (ADMIN only)
/api/v1/admin/dashboard                 GET        (ADMIN only)

Repository Version:
0.5.0

Next Prompt:
Not yet defined (Monaco Editor / Execution Engine / Student Portal are
candidates per the Master Context's pending list).
