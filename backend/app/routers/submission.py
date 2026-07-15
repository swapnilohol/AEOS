from fastapi import (
    APIRouter,
    Depends
)
from app.executor.runner import run_python_code
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.submission import Submission
from app.models.user import User
from app.schemas.submission import (SubmissionCreate
)
from app.auth.dependencies import (
    get_current_user
)
from app.services.executor import (
    execute_python
)
from app.models.testcase import TestCase
from app.models.problem import Problem
router = APIRouter(
    prefix="/submissions",
    tags=["Submissions"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def health():

    return {
        "message":
        "Submission API working"
    }


@router.post("/")
def submit_code(
    submission: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    new_submission = Submission(
        user_id=current_user.id,
        problem_id=submission.problem_id,
        source_code=submission.source_code,
        language=submission.language,
        status="PENDING"
    )

    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    testcases = (
        db.query(TestCase)
        .filter(
            TestCase.problem_id
            ==
            submission.problem_id
        )
        .all()
    )

    passed = 0
    total = len(testcases)

    for tc in testcases:

        result = execute_python(
            submission.source_code,
            tc.input_data
        )

        output = result["output"].strip()
        expected = tc.expected_output.strip()

        if output == expected:
            passed += 1

    problem = (
        db.query(Problem)
        .filter(
            Problem.id ==
            submission.problem_id
        )
        .first()
    )

    if passed == total:
        new_submission.status = "ACCEPTED"
        new_submission.score = (
            problem.points if problem else 0
        )
    else:
        new_submission.status = "WRONG_ANSWER"
        new_submission.score = 0

    new_submission.output = (
        f"{passed}/{total} testcases passed"
    )

    db.commit()
    db.refresh(new_submission)

    return {
        "message": "Code submitted",
        "submission_id": new_submission.id,
        "status": new_submission.status,
        "output": new_submission.output,
        "score": new_submission.score
    }
@router.get("/my")
def my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    submissions = (
        db.query(Submission)
        .filter(
            Submission.user_id
            ==
            current_user.id
        )
        .all()
    )

    return submissions
