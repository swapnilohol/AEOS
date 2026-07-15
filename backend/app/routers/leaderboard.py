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
            func.sum(
                Submission.score
            ).label("score")
        )
        .join(
            Submission,
            User.id == Submission.user_id
        )
        .group_by(
            User.username
        )
        .all()
    )

    return [
        {
            "username": row.username,
            "score": row.score
        }
        for row in data
    ]
