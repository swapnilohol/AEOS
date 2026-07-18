# AEOS Demo Workflow 🚀

## Student Flow

### 1. Registration

Student creates an account using the registration page.

Features:
- Username creation
- Email authentication
- Secure password hashing


---

## 2. Login

Student logs into AEOS using credentials.

System:
- Validates user credentials
- Generates JWT token
- Provides role-based access


---

## 3. Dashboard

Student dashboard displays:

- Username
- Total submissions
- Solved problems
- Total score
- Leaderboard rank


---

## 4. Problem Selection

Student selects an engineering problem.

Problem contains:

- Description
- Difficulty
- Points
- Test cases


---

## 5. Code Editor

Student writes solution using Monaco Editor.

Supported execution:

- Python
- Java
- C++
- JavaScript


---

## 6. Code Submission

When student submits:

Flow:
Frontend
|
FastAPI Backend
|
Submission Service
|
Execution Engine
|
Test Case Validation



---

## 7. Execution Engine

The platform:

- Creates isolated execution environment
- Runs submitted code
- Compares output
- Generates result


Example:


Status: ACCEPTED

Score: 100

Output:
1/1 testcases passed



---

## 8. Leaderboard

Scores are automatically updated.

Leaderboard shows:

- Rank
- Username
- Solved problems
- Total score


---

# Admin Flow

Admin can:

- Login
- View platform statistics
- Create problems
- Add test cases
- Monitor submissions


---

# Complete Demo Sequence

1. Student Registration
2. Student Login
3. Open Dashboard
4. Solve Problem
5. Submit Code
6. Receive Score
7. View Leaderboard
8. Admin Reviews Activity


---

# Result

AEOS evaluates students through real coding challenges instead of traditional MCQ assessments.
Step 3: Save
Ctrl + O
Enter
Ctrl + X
Step 4: Git push
git add docs/DEMO_WORKFLOW.md

git commit -m "Add AEOS demo workflow documentation"

git push origin main
