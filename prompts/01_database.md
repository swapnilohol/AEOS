# DATABASE MODULE

Load:

00_MASTER_CONTEXT.md
01_GLOBAL_RULES.md
02_ARCHITECTURE.md
03_CODING_STANDARDS.md
context/project_state.md

Objective:

Create database foundation for AI Elite Internship Hackathon Platform.

Database:
- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- UUID Primary Keys

Entities:

1. roles
2. users
3. hackathons
4. problems
5. problem_tests
6. submissions
7. execution_results
8. scores
9. violations
10. leaderboard_entries

Seed Data:

Roles:
- ADMIN
- STUDENT

Problems:
1. Semantic Resume Intelligence
2. Multi-Agent Interview Scheduler
3. AI Fraud Detection Engine
4. Decision Intelligence Agent

Generate:

- SQLAlchemy Models
- Alembic Migrations
- Seed Scripts
- Database Session
- Base Models

Do NOT generate APIs.

Repository Version:
0.2.0

Next Prompt:
prompts/02_auth.md
