from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.testcase import TestCase
from app.schemas.testcase import (
    TestCaseCreate
)

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
    db: Session = Depends(get_db)
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
