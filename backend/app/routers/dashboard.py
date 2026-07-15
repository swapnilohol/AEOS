from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.models.submission import Submission
from app.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def student_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    total_submissions = (
        db.query(Submission)
        .filter(
            Submission.user_id == current_user.id
        )
        .count()
    )

    solved = (
        db.query(Submission)
        .filter(
            Submission.user_id == current_user.id,
            Submission.status == "ACCEPTED"
        )
        .count()
    )

    score = (
        db.query(Submission)
        .filter(
            Submission.user_id == current_user.id
        )
        .with_entities(
            Submission.score
        )
        .all()
    )

    total_score = sum(
        s[0] or 0 for s in score
    )

    return {
        "username": current_user.username,
        "total_submissions": total_submissions,
        "solved_problems": solved,
        "total_score": total_score
    }
