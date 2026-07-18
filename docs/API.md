# AEOS API Documentation

## Base URL
http://localhost:8000


---

# 1. Authentication APIs

## Register User

**POST**


/auth/register


### Request

```json
{
  "username": "student01",
  "email": "student@gmail.com",
  "password": "123456"
}
Response
{
  "message": "User created successfully"
}
Login User

POST

/auth/login
Request

Form Data:

username=email
password=password
Response
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}
Current User

GET

/auth/me

Header:

Authorization: Bearer TOKEN

Response:

{
  "username": "swapnil04",
  "role": "STUDENT"
}
2. Problem APIs
Get All Problems

GET

/problems/all

Response:

[
 {
  "id":1,
  "title":"Two Sum",
  "difficulty":"EASY",
  "points":100
 }
]
Get Problem Details

GET

/problems/{id}

Example:

/problems/1
Create Problem (Admin)

POST

/problems/

Request:

{
"title":"Addition",
"difficulty":"EASY",
"points":100
}
3. Test Case APIs
Create Test Case

POST

/testcases/

Request:

{
"problem_id":1,
"input_data":{
"nums":[2,7],
"target":9
},
"expected_output":"[0,1]"
}
4. Submission APIs
Submit Code

POST

/submissions/

Request:

{
"problem_id":1,
"source_code":"python code",
"language":"python"
}

Response:

{
"status":"ACCEPTED",
"score":100
}
My Submissions

GET

/submissions/my

Header:

Authorization: Bearer TOKEN
5. Leaderboard API
Get Leaderboard

GET

/leaderboard/

Response:

[
{
"rank":1,
"username":"swapnil04",
"score":300
}
]
6. Dashboard APIs
Student Dashboard

GET

/dashboard

Response:

{
"username":"swapnil04",
"total_submissions":6,
"solved_problems":2,
"score":200
}
Admin Dashboard

GET

/admin/dashboard

Response:

{
"total_users":6,
"total_problems":5,
"total_submissions":22
}
7. Admin APIs
Create Student

POST

/admin/users
Platform Statistics

GET

/admin/stats
Authentication

All protected APIs require:

Authorization: Bearer JWT_TOKEN
API Status
Module	Status
Authentication	Completed
Student Management	Completed
Problem Management	Completed
Test Cases	Completed
Code Execution	Completed
Scoring	Completed
Leaderboard	Completed
Admin Dashboard	Completed

Save:
