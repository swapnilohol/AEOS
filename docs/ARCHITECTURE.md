# AEOS Architecture 🚀

## System Overview

AEOS (AI Engineering Operating System) is a coding assessment platform that evaluates students through real programming challenges.

The system consists of:

- Next.js frontend
- FastAPI backend
- PostgreSQL database
- Redis cache
- Docker-based execution engine


## High Level Architecture
            Student / Admin
                  |
                  |
          Next.js Frontend
    (TypeScript + Tailwind + Monaco)
                  |
                  |
          FastAPI Backend
                  |
    ----------------------------
    |             |            |
PostgreSQL Redis Code Executor
Database Cache Docker Sandbox
|
|
Users, Problems,
Test Cases,
Submissions,
Scores


## Component Description

### Frontend

Technology:

- Next.js
- TypeScript
- Tailwind CSS
- Monaco Editor

Responsibilities:

- User interface
- Authentication screens
- Problem workspace
- Code submission
- Dashboard display


### Backend

Technology:

- FastAPI
- Python
- SQLAlchemy

Responsibilities:

- Authentication
- User management
- Problem APIs
- Submission handling
- Score calculation


### Database

PostgreSQL stores:

- Users
- Problems
- Test Cases
- Submissions
- Scores


### Execution Engine

Responsibilities:

1. Receive submitted code
2. Execute inside sandbox
3. Run against test cases
4. Compare output
5. Return result


## Data Flow
User writes code
|
|
Submit Solution
|
|
FastAPI API
|
|
Execution Engine
|
|
Test Case Validation
|
|
Score Generated
|
|
Leaderboard Updated


## Deployment Architecture
          Internet

             |
             |

          Nginx

    ----------------

    |              |
Frontend Backend
Next.js FastAPI

                  |

         ----------------

         PostgreSQL
         Redis
         Docker

## Security

- JWT Authentication
- Password hashing using bcrypt
- Role Based Access Control
- Isolated code execution
- API authorization


## Future Improvements

- Multi-language execution
- AI code review
- Cloud deployment
- Advanced analytics
