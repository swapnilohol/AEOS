# STUDENT MANAGEMENT MODULE

Load:

00_MASTER_CONTEXT.md
01_GLOBAL_RULES.md
02_ARCHITECTURE.md
03_CODING_STANDARDS.md
prompts/01_database.md
prompts/02_auth.md
context/project_state.md

Objective:

Implement Production Ready Student Management System.

Features:
- Student Registration
- Student Profile Management
- Student CRUD Operations
- Student Search
- Student Dashboard
- JWT Authentication Integration
- Role Based Access Control

Database:

Create student_profiles table (id, user_id, student_id, college_name,
department, semester, graduation_year, phone_number, skills, resume_url,
created_at, updated_at). user_id and student_id unique.

API:

/api/v1/students            POST    (admin) create student
/api/v1/students            GET     (admin) list/search students
/api/v1/students/{id}       GET     (admin) student details
/api/v1/students/{id}       PUT     (admin) update student
/api/v1/students/{id}       DELETE  (admin) delete student
/api/v1/students/me         GET     (student) own profile
/api/v1/students/me         PUT     (student) update own profile
/api/v1/students/dashboard  GET     (student) dashboard

Validation:

- Email required/unique/valid
- Password: 8+ chars, upper/lower/number/special
- student_id required/unique
- semester 1-8
- phone: valid mobile number

Do not modify Database or Authentication modules.
Do not generate Admin Dashboard, Problem Management, or Analytics.

Repository Version:
0.4.0

Next Prompt:
TBD
