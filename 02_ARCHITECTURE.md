# 02_ARCHITECTURE.md

````md id="aeos-architecture-v1"
# =============================================================================
#
#                 AI ENGINEERING OPERATING SYSTEM (AEOS)
#
#                           SYSTEM ARCHITECTURE
#
# =============================================================================

Version
-------
1.0

Depends On
----------
00_MASTER_CONTEXT.md

01_GLOBAL_RULES.md

Project
-------
TheGCPal Labs AI Elite Internship Hackathon Platform

Pilot
-----
Newton Institute of Science and Technology

Target
------
10 Concurrent Students

Architecture Style
------------------

Modular Monolith

Deployment
----------

Single VPS

# =============================================================================
# SYSTEM OVERVIEW
# =============================================================================

The platform is designed to conduct a live AI internship assessment.

Students access the platform through a browser.

Administrators manage problems and monitor progress.

Submissions are executed inside isolated Docker containers.

Scores are generated automatically.

The architecture intentionally avoids enterprise complexity.

# =============================================================================
# HIGH LEVEL ARCHITECTURE
# =============================================================================

```text
Students/Admin
       │
       ▼
Cloudflare + HTTPS
       │
       ▼
      Nginx
       │
       ▼
 ┌─────────────────────┐
 │     Next.js App     │
 └─────────────────────┘
       │
 REST APIs
       │
       ▼
 ┌─────────────────────┐
 │      FastAPI        │
 └─────────────────────┘
       │
 ┌─────────────┬───────────────┐
 │             │               │
 ▼             ▼               ▼

PostgreSQL    Redis      Execution Service
                               │
                               ▼
                       Docker Sandbox
````

# =============================================================================

# SYSTEM COMPONENTS

# =============================================================================

Frontend

* Student Portal
* Admin Portal
* Monaco Editor
* Leaderboard
* Timer
* Result Viewer

Backend

* Authentication
* Problem Management
* Submission Management
* Evaluation Service
* Leaderboard Service
* Violation Logging

Infrastructure

* PostgreSQL
* Redis
* Docker Executor
* Nginx
* Cloudflare

# =============================================================================

# FRONTEND ARCHITECTURE

# =============================================================================

Technology

* Next.js 15
* TypeScript
* TailwindCSS

Architecture

```text
App Router

Pages
│
├── Student
├── Admin
├── Auth
├── Leaderboard
└── Public
```

Frontend Layers

```text
Pages
 ↓
Components
 ↓
Hooks
 ↓
API Client
 ↓
Backend APIs
```

Folder Structure

```text
apps/frontend/

app/
components/
hooks/
lib/
services/
types/
styles/
```

Guidelines

* Prefer Server Components
* Minimal Client State
* Reusable Components
* Thin Pages
* API driven UI

# =============================================================================

# BACKEND ARCHITECTURE

# =============================================================================

Technology

* FastAPI
* Python 3.12

Architecture Pattern

Modular Monolith

Layers

```text
API
 ↓
Services
 ↓
Repositories
 ↓
Database
```

Folder Structure

```text
apps/backend/

app/

api/
core/
db/
models/
schemas/
services/
repositories/
middlewares/
utils/
```

Responsibilities

API Layer

* Request handling
* Validation
* Authentication

Service Layer

* Business rules
* Scoring
* Evaluation

Repository Layer

* Database access

Core Layer

* Config
* Security
* Logging

# =============================================================================

# DATABASE ARCHITECTURE

# =============================================================================

Database

PostgreSQL

Architecture

Single Database

Schema Philosophy

* Normalized
* Minimal joins
* UUID primary keys
* Indexed relationships

Entities

```text
users
roles
hackathons
problems
problem_tests
submissions
execution_results
scores
violations
leaderboards
```

Entity Relationship

```text
User
 │
 ├── Submission
 │       │
 │       └── ExecutionResult
 │
 └── Score

Hackathon
 │
 └── Problem
          │
          └── ProblemTest
```

Indexes

* email
* user_id
* hackathon_id
* problem_id
* submission_id

# =============================================================================

# EXECUTION ENGINE ARCHITECTURE

# =============================================================================

Purpose

Secure execution of student code.

Technology

Docker Containers

Architecture

```text
Submission
      │
      ▼
Execution Queue
      │
      ▼
Sandbox Container
      │
      ▼
Test Execution
      │
      ▼
JSON Result
      │
      ▼
Database
```

Responsibilities

* Create isolated containers
* Execute code safely
* Enforce limits
* Return results

Restrictions

CPU Limit

Memory Limit

Execution Timeout

No Network Access

Read-only runtime where possible.

# =============================================================================

# EXECUTION FLOW

# =============================================================================

```text
Student Submit
       │
       ▼
Backend API
       │
       ▼
Executor Service
       │
       ▼
Docker Sandbox
       │
       ▼
Run Public Tests
       │
       ▼
Run Hidden Tests
       │
       ▼
Generate Results
       │
       ▼
Store Results
       │
       ▼
Leaderboard Update
```

# =============================================================================

# DEPLOYMENT ARCHITECTURE

# =============================================================================

Infrastructure

Single VPS

Recommended Server

```text
4 vCPU
8 GB RAM
80 GB SSD
Ubuntu 24.04
```

Deployment Stack

```text
Cloudflare
      │
      ▼
HTTPS
      │
      ▼
Nginx
      │
      ▼
Docker Compose
      │
      ▼
Services
```

Services

```text
frontend
backend
executor
postgres
redis
nginx
```

Deployment Diagram

```text
Internet
    │
    ▼
Cloudflare
    │
    ▼
Nginx
    │
 ┌──┴────────────┐
 ▼               ▼

Frontend      Backend
                   │
            ┌──────┴──────┐
            ▼             ▼

        PostgreSQL      Redis
                   │
                   ▼

            Executor Service
```

# =============================================================================

# FOLDER STRUCTURE

# =============================================================================

```text
AI-Engineering-OS/

apps/
│
├── frontend/
│
├── backend/
│
└── executor/

packages/
│
└── shared/

docs/

scripts/

infrastructure/

context/

prompts/
```

Frontend

```text
frontend/

app/
components/
hooks/
lib/
services/
types/
```

Backend

```text
backend/

app/
api/
core/
db/
models/
schemas/
services/
repositories/
middlewares/
utils/
```

Executor

```text
executor/

runner/
sandbox/
images/
utils/
```

# =============================================================================

# API FLOW

# =============================================================================

Authentication Flow

```text
Login
  │
  ▼
FastAPI
  │
  ▼
JWT
  │
  ▼
Frontend Session
```

Hackathon Flow

```text
Student Login
      │
      ▼
Load Problems
      │
      ▼
Start Timer
      │
      ▼
Code Submission
      │
      ▼
Execution
      │
      ▼
Scoring
      │
      ▼
Leaderboard
```

Admin Flow

```text
Admin Login
      │
      ▼
Create Hackathon
      │
      ▼
Upload Problems
      │
      ▼
Monitor Students
      │
      ▼
Export Results
```

# =============================================================================

# REST API STRUCTURE

# =============================================================================

```text
/api/v1/auth

/api/v1/users

/api/v1/hackathons

/api/v1/problems

/api/v1/submissions

/api/v1/executions

/api/v1/leaderboard

/api/v1/reports

/api/v1/violations
```

# =============================================================================

# PERFORMANCE TARGETS

# =============================================================================

Concurrent Users

10

Target API Response

< 300 ms

Submission Processing

< 5 sec

Docker Startup

< 2 sec

Page Load

< 2 sec

# =============================================================================

# SECURITY PRINCIPLES

# =============================================================================

* JWT authentication
* Input validation
* Rate limiting
* Docker isolation
* No container networking
* Environment variables only
* HTTPS everywhere
* Structured logging

# =============================================================================

# FUTURE SCALE PATH

# =============================================================================

Current

10 Students

Future

50 Students

100 Students

Scale Strategy

1.

Separate executor service

2.

Managed PostgreSQL

3.

Redis queues

4.

Horizontal backend scaling

No rewrite required.

# =============================================================================

# FINAL PRINCIPLE

# =============================================================================

This architecture is intentionally simple.

Goal:

Launch a reliable MVP in 3 days.

Avoid overengineering.

Ship first.

Iterate later.

# =============================================================================

```
```
