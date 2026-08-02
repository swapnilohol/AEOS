from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.problem import Problem
from app.models.submission import Submission

from app.auth.roles import require_role
from app.auth.hashing import hash_password

from app.schemas.user import (
    UserCreate,
    UserResponse
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)
@router.get("/dashboard")
def admin_dashboard(
    user: User = Depends(
        require_role("ADMIN")
    )
):

    return {
        "message": "Welcome Admin",
        "user": user.email
    }


@router.post(
    "/users",
    response_model=UserResponse
)
def create_student(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(
        require_role("ADMIN")
    )
):

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(
            user_data.password
        ),
        role="STUDENT"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
@router.get("/stats")
def admin_stats(
    db: Session = Depends(get_db),
    user: User = Depends(
        require_role("ADMIN")
    )
):

    total_users = db.query(User).count()
    total_problems = db.query(Problem).count()
    total_submissions = db.query(Submission).count()

    return {
        "total_users": total_users,
        "total_problems": total_problems,
        "total_submissions": total_submissions
    }
@router.get("/submissions")
def admin_submissions(
    db: Session = Depends(get_db),
    user: User = Depends(
        require_role("ADMIN")
    )
):

    submissions = (
        db.query(
            Submission,
            User.username,
            Problem.title
        )
        .join(
            User,
            Submission.user_id == User.id
        )
        .join(
            Problem,
            Submission.problem_id == Problem.id
        )
        .order_by(
            Submission.id.desc()
        )
        .limit(20)
        .all()
    )


    return [
        {
            "id": sub.id,
            "username": username,
            "problem": title,
            "language": sub.language,
            "status": sub.status,
            "score": sub.score
        }
        for sub, username, title in submissions
    ]
