# =============================================================================
#
#                 AI ENGINEERING OPERATING SYSTEM (AEOS)
#
#                         CODING STANDARDS
#
# =============================================================================

Version
-------
1.0

Depends On
----------

00_MASTER_CONTEXT.md
01_GLOBAL_RULES.md
02_ARCHITECTURE.md

Applies To
----------

Entire Repository

Project
-------

TheGCPal Labs AI Elite Internship Hackathon Platform

# =============================================================================
# PURPOSE
# =============================================================================

This document defines mandatory coding standards for:

- Maintainability
- Readability
- Security
- Fast onboarding
- AI-assisted development
- Token efficiency
- Consistent architecture

All engineers and AI agents must follow these rules.

# =============================================================================
# GENERAL ENGINEERING PRINCIPLES
# =============================================================================

Prefer:

✓ Simple code
✓ Explicit code
✓ Small functions
✓ Predictable behavior
✓ Reusable components

Avoid:

✗ Clever code
✗ Deep inheritance
✗ Premature optimization
✗ Hidden side effects
✗ Large files
✗ Unnecessary abstractions

# =============================================================================
# FILE SIZE STANDARDS
# =============================================================================

Recommended Limits

Function: < 50 lines  
Class: < 300 lines  
File: < 400 lines  

Maximum nesting: 3 levels  
Maximum parameters: 5  
Maximum cyclomatic complexity: 10

# =============================================================================
# PYTHON CODING STANDARDS
# =============================================================================

Python Version: 3.12  
Style Guide: PEP8  
Formatting: Black  
Linting: Ruff  
Type Checking: mypy

Prefer:
- Type hints
- Dataclasses/Pydantic
- Explicit imports

Avoid:
- Wildcard imports
- Circular dependencies
- Global mutable state

# =============================================================================
# TYPESCRIPT STANDARDS
# =============================================================================

Language: TypeScript Strict Mode

Avoid:
- any
- implicit typing
- giant components

Prefer:
- explicit interfaces
- reusable hooks
- composition

# =============================================================================
# DATABASE STANDARDS
# =============================================================================

Database: PostgreSQL  
Primary Keys: UUID  
Migration Tool: Alembic

Rules:

✓ Normalize schema  
✓ Index foreign keys  
✓ Use timestamps  

# =============================================================================
# LOGGING STANDARDS
# =============================================================================

Use structured JSON logging.

Never log:

✗ Passwords  
✗ Tokens  
✗ Secrets  

# =============================================================================
# TESTING STANDARDS
# =============================================================================

Backend: pytest  
Frontend: Vitest  

Coverage Goal: 70%+

# =============================================================================
# SECURITY STANDARDS
# =============================================================================

Authentication: JWT

Rules:

✓ Validate input  
✓ HTTPS only  
✓ Environment variables only  

Avoid:

✗ Hardcoded secrets  
✗ Dynamic SQL  

# =============================================================================
# DOCKER STANDARDS
# =============================================================================

Services:

- frontend
- backend
- executor
- postgres
- redis

Preferred Images:

Python: python:3.12-slim  
Node: node:22-alpine

# =============================================================================
# DOCUMENTATION STANDARDS
# =============================================================================

Every module must update:

- README
- API Docs
- Environment Docs
- Repository State

# =============================================================================
# FINAL PRINCIPLE
# =============================================================================

Code should be:

Simple.  
Predictable.  
Maintainable.

Working software is more important than perfect software.

Ship first. Improve later.

# =============================================================================