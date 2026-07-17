# AUTHENTICATION MODULE

Load:

00_MASTER_CONTEXT.md
01_GLOBAL_RULES.md
02_ARCHITECTURE.md
03_CODING_STANDARDS.md
prompts/01_database.md
context/project_state.md

Objective:

Implement production-ready authentication system for TheGCPal Labs AI Elite
Internship Hackathon Platform.

Features:
- JWT Authentication (access + refresh)
- Admin Login / Student Login
- Password Hashing (bcrypt)
- Refresh Token Management (rotation, hashed at rest)
- Role Based Access Control (ADMIN, STUDENT)
- Protected APIs
- Logout Flow
- Session Security (lockout, rate limiting)

Database changes:

Update users table with: username, role, is_active, last_login_at,
refresh_token_hash, failed_login_attempts, locked_until.

API:

/api/v1/auth/login
/api/v1/auth/refresh
/api/v1/auth/logout
/api/v1/auth/me
/api/v1/auth/change-password
/api/v1/auth/admin/create-student

Do NOT regenerate Bootstrap or Database modules.

Repository Version:
0.3.0

Next Prompt:
prompts/03_admin_portal.md
