from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

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
    db.query(
        Submission.problem_id
    )
    .filter(
        Submission.user_id == current_user.id,
        Submission.status == "ACCEPTED"
    )
    .distinct()
    .count()
)

    total_score = solved * 100

    total_problems = (
        db.query(Submission.problem_id)
        .filter(
            Submission.user_id == current_user.id
        )
        .distinct()
        .count()
    )


    rank_data = (
        db.query(
            User.username,
            func.sum(
                Submission.score
            ).label("score")
        )
        .join(
            Submission,
            User.id == Submission.user_id
        )
        .filter(
    User.role == "STUDENT"
)
        .group_by(
            User.username
        )
        .order_by(
            func.sum(
                Submission.score
            ).desc()
        )
        .all()
    )


    rank = 0

    for index, user in enumerate(rank_data):
        if user.username == current_user.username:
            rank = index + 1
    return {
    "username": current_user.username,
    "total_submissions": total_submissions,
    "attempted_problems": total_problems,
    "solved_problems": solved,
    "total_score": total_score,
    "rank": rank
}
