# 01_GLOBAL_RULES.md

```md
# =============================================================================
#
#                 AI ENGINEERING OPERATING SYSTEM (AEOS)
#
#                         GLOBAL ENGINEERING RULES
#
# =============================================================================

Version
-------
1.0

Depends On
----------
00_MASTER_CONTEXT.md

Applies To
----------
Entire Repository

# =============================================================================
# PURPOSE
# =============================================================================

This document defines the mandatory engineering rules for building:

TheGCPal Labs AI Elite Internship Hackathon Platform.

These rules exist to:

- maintain architectural consistency
- minimize token usage
- reduce AI hallucinations
- improve maintainability
- enable fast delivery
- support context recovery

All engineers and AI agents must follow these rules.

# =============================================================================
# CORE PRINCIPLES
# =============================================================================

Priority Order

1. Working Software
2. Simplicity
3. Maintainability
4. Security
5. Performance
6. Future Scalability

Never sacrifice simplicity for theoretical scale.

MVP first.

# =============================================================================
# DEVELOPMENT WORKFLOW
# =============================================================================

Every module must follow this sequence.

STEP 1

Understand requirement.

STEP 2

Review current repository state.

STEP 3

Review existing files.

STEP 4

Design minimal solution.

STEP 5

List affected files.

STEP 6

Implement code.

STEP 7

Generate tests.

STEP 8

Update documentation.

STEP 9

Run validation.

STEP 10

Update repository state.

STEP 11

Commit changes.

STEP 12

Stop.

Never continue automatically.

# =============================================================================
# MODULE DEVELOPMENT RULE
# =============================================================================

Only ONE module may be implemented at a time.

Examples:

GOOD

Database only.

Authentication only.

Leaderboard only.

BAD

Database + Authentication + Dashboard.

Large changes increase hallucination risk.

# =============================================================================
# REPOSITORY DISCIPLINE
# =============================================================================

Never regenerate repository structure.

Never rewrite working code.

Never duplicate modules.

Never move files without reason.

Never create unnecessary abstractions.

Always modify the smallest number of files.

Prefer patches.

# =============================================================================
# FILE SIZE RULES
# =============================================================================

Recommended Limits

Function

< 50 lines

Class

< 300 lines

File

< 400 lines

Avoid deeply nested code.

Maximum nesting:

3 levels.

# =============================================================================
# CODING DISCIPLINE
# =============================================================================

Always prefer:

Readable code

Predictable code

Simple code

Avoid:

Magic values

Long functions

Unnecessary inheritance

Premature optimization

Hidden side effects

Complex design patterns

MVP code should be boring and maintainable.

# =============================================================================
# NAMING RULES
# =============================================================================

Files

snake_case

Python

snake_case

TypeScript Variables

camelCase

Components

PascalCase

Database Tables

snake_case_plural

Examples:

users

submissions

problem_tests

API Prefix:

/api/v1

# =============================================================================
# ERROR HANDLING RULES
# =============================================================================

Never swallow exceptions.

Every API must return:

success

message

data

errors

Use global exception handling.

Always log errors.

Never expose stack traces to clients.

# =============================================================================
# DATABASE RULES
# =============================================================================

Use migrations.

No direct schema edits.

Index:

foreign keys

search fields

timestamps if needed

Avoid unnecessary joins.

Avoid duplicated data.

Prefer UUIDs.

# =============================================================================
# API RULES
# =============================================================================

REST only.

JSON only.

Version every API.

Validate every request.

Validate every response.

Document APIs.

Avoid breaking contracts.

# =============================================================================
# FRONTEND RULES
# =============================================================================

Use reusable components.

Avoid unnecessary global state.

Keep pages thin.

Move logic into hooks/services.

Prefer server components.

Avoid large client bundles.

No unnecessary libraries.

# =============================================================================
# BACKEND RULES
# =============================================================================

Keep endpoints small.

Keep services small.

Prefer explicit dependencies.

Use type hints.

Use Pydantic models.

Use structured logging.

# =============================================================================
# SECURITY RULES
# =============================================================================

Never trust input.

Never store secrets in code.

Use environment variables.

Sanitize user data.

Validate JWT.

Rate limit authentication APIs.

Avoid unnecessary permissions.

# =============================================================================
# DOCUMENTATION RULES
# =============================================================================

Every module must update:

README

Environment Variables

API Documentation

Repository State

No undocumented features.

Documentation is mandatory.

# =============================================================================
# GIT WORKFLOW
# =============================================================================

Branch Strategy

main

production-ready code only

feature/*

all development work

Examples:

feature/database

feature/auth

feature/editor

# =============================================================================
# COMMIT RULES
# =============================================================================

One logical change per commit.

Commit immediately after module completion.

Format:

type(scope): message

Examples:

feat(database): create initial schema

feat(auth): implement jwt login

feat(editor): integrate monaco

fix(timer): correct countdown issue

docs(readme): update setup instructions

# =============================================================================
# AI COLLABORATION RULES
# =============================================================================

Claude acts as:

Architect

Engineer

Reviewer

Mentor

Technical Writer

Claude must:

Generate one module only.

Stop after completion.

Never regenerate unchanged files.

Never repeat context.

Never invent missing APIs.

Create dependencies first.

Explain architecture briefly.

Produce production-ready code.

# =============================================================================
# TOKEN OPTIMIZATION RULES
# =============================================================================

Always optimize for token efficiency.

Rules:

1.

Never regenerate unchanged files.

2.

Never repeat requirements.

3.

Never repeat repository tree.

4.

Prefer diffs.

5.

Prefer concise explanations.

6.

Summarize context every few prompts.

7.

Repository summaries must remain under 300 tokens.

# =============================================================================
# CONTEXT RECOVERY RULES
# =============================================================================

Every module ends with:

Repository Version

Completed Modules

Pending Modules

Files Added

Files Modified

Database Version

API Version

Known Issues

Next Prompt

This allows Claude sessions to continue after context loss.

# =============================================================================
# REVIEW CHECKLIST
# =============================================================================

Before completing a module verify:

[ ] Builds successfully

[ ] Docker builds

[ ] Tests pass

[ ] No syntax errors

[ ] No duplicate code

[ ] Documentation updated

[ ] Environment variables documented

[ ] API contracts documented

[ ] Logging exists

[ ] Error handling exists

[ ] Repository state updated

# =============================================================================
# DEFINITION OF DONE
# =============================================================================

A task is complete only if:

✓ Feature works.

✓ Tests pass.

✓ Documentation updated.

✓ Docker builds.

✓ Repository state updated.

✓ Commit created.

Otherwise:

TASK IS NOT COMPLETE.

# =============================================================================
# FINAL ENGINEERING PRINCIPLE
# =============================================================================

Working software is more valuable than perfect software.

Prefer:

simple > clever

maintainable > abstract

shipping > theorizing

Launch in 3 days.

Iterate later.

# =============================================================================
```
