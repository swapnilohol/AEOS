from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal
from app.models.submission import Submission
from app.models.user import User


router = APIRouter(
    prefix="/leaderboard",
    tags=["Leaderboard"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.get("/")
def leaderboard(
    db: Session = Depends(get_db)
):

    data = (
        db.query(
            User.username,

            func.count(
                func.distinct(
                    Submission.problem_id
                )
            ).label("solved"),

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

        .filter(
            Submission.status == "ACCEPTED"
        )

        .group_by(
            User.username
        )

        .order_by(
            func.count(
                func.distinct(
                    Submission.problem_id
                )
            ).desc()
        )

        .all()
    )


    return [
        {
            "rank": index + 1,
            "username": row.username,
            "solved": row.solved,
            "score": row.solved * 100
        }

        for index, row in enumerate(data)
    ]
