from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.testcase import TestCase
from app.models.problem import Problem
from app.models.user import User

from app.schemas.testcase import TestCaseCreate
from app.auth.roles import require_role


router = APIRouter(
    prefix="/testcases",
    tags=["Test Cases"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_testcase(
    testcase: TestCaseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_role("ADMIN")
    )
):

    new_testcase = TestCase(
        problem_id=testcase.problem_id,
        input_data=testcase.input_data,
        expected_output=testcase.expected_output,
        is_hidden=testcase.is_hidden
    )

    db.add(new_testcase)
    db.commit()
    db.refresh(new_testcase)

    return new_testcase


@router.get("/")
def get_testcases(
    db: Session = Depends(get_db),
    user: User = Depends(
        require_role("ADMIN")
    )
):

    data = (
        db.query(
            TestCase,
            Problem.title
        )
        .join(
            Problem,
            TestCase.problem_id == Problem.id
        )
        .all()
    )

    return [
        {
            "id": tc.id,
            "problem": title,
            "input": tc.input_data,
            "expected_output":
                tc.expected_output,
            "hidden":
                tc.is_hidden
        }
        for tc, title in data
    ]


@router.delete("/{testcase_id}")
def delete_testcase(
    testcase_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_role("ADMIN")
    )
):

    tc = (
        db.query(TestCase)
        .filter(
            TestCase.id == testcase_id
        )
        .first()
    )

    if not tc:
        return {
            "error":
            "Testcase not found"
        }

    db.delete(tc)
    db.commit()

    return {
        "message":
        "Deleted"
    }
