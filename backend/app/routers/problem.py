from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.problem import Problem
from app.schemas.problem import (
    ProblemCreate,
    ProblemResponse
)
from app.models.user import User
from app.auth.roles import require_role


router = APIRouter(
    prefix="/problems",
    tags=["Problems"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/",
    response_model=list[ProblemResponse]
)
def get_problems(
    db: Session = Depends(get_db)
):

    return db.query(Problem).all()


@router.post("/")
def create_problem(
    problem: ProblemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_role("ADMIN")
    )
):

    new_problem = Problem(
        title=problem.title,
        description=problem.description,
        difficulty=problem.difficulty,
        points=problem.points
    )

    db.add(new_problem)
    db.commit()
    db.refresh(new_problem)

    return {
        "message":
        "Problem created",
        "id":
        new_problem.id
    }
@router.get("/all")
def list_problems(
    db: Session = Depends(get_db)
):

    problems = (
        db.query(Problem)
        .all()
    )

    return problems
@router.get("/{problem_id}")
def get_problem(
    problem_id: int,
    db: Session = Depends(get_db)
):

    problem = (
        db.query(Problem)
        .filter(
            Problem.id == problem_id
        )
        .first()
    )

    if not problem:
        return {
            "error": "Problem not found"
        }

    return problem
@router.delete("/{problem_id}")
def delete_problem(
    problem_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_role("ADMIN")
    )
):

    problem = (
        db.query(Problem)
        .filter(
            Problem.id == problem_id
        )
        .first()
    )

    if not problem:
        return {
            "error": "Problem not found"
        }

    db.delete(problem)
    db.commit()

    return {
        "message": "Problem deleted"
    }
@router.put("/{problem_id}")
def update_problem(
    problem_id: int,
    problem_data: ProblemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_role("ADMIN")
    )
):

    problem = (
        db.query(Problem)
        .filter(
            Problem.id == problem_id
        )
        .first()
    )

    if not problem:
        return {
            "error": "Problem not found"
        }

    problem.title = problem_data.title
    problem.description = problem_data.description
    problem.difficulty = problem_data.difficulty
    problem.points = problem_data.points

    db.commit()
    db.refresh(problem)

    return {
        "message": "Problem updated",
        "id": problem.id
    }
