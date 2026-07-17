"""
Seed script for baseline reference data.

Usage:
    python -m app.db.seed

Idempotent: safe to run multiple times.
"""
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models import Hackathon, Problem, Role, RoleName

PILOT_HACKATHON_TITLE = "AI Elite Internship Hackathon"

PROBLEM_TITLES = [
    "Semantic Resume Intelligence",
    "Multi-Agent Interview Scheduler",
    "AI Fraud Detection Engine",
    "Decision Intelligence Agent",
]


def seed_roles(db) -> None:
    for role_name in (RoleName.ADMIN, RoleName.STUDENT):
        exists = db.query(Role).filter(Role.name == role_name.value).first()
        if not exists:
            db.add(Role(name=role_name.value))


def seed_hackathon_and_problems(db) -> None:
    hackathon = db.query(Hackathon).filter(Hackathon.title == PILOT_HACKATHON_TITLE).first()
    if not hackathon:
        hackathon = Hackathon(
            title=PILOT_HACKATHON_TITLE,
            description="Pilot hackathon for Newton Institute of Science and Technology.",
            is_active=True,
        )
        db.add(hackathon)
        db.flush()

    for index, title in enumerate(PROBLEM_TITLES):
        exists = (
            db.query(Problem)
            .filter(Problem.hackathon_id == hackathon.id, Problem.title == title)
            .first()
        )
        if not exists:
            db.add(
                Problem(
                    hackathon_id=hackathon.id,
                    title=title,
                    description=f"Problem statement for '{title}' to be finalized by admins.",
                    max_score=100,
                    order_index=index,
                )
            )


def run_seed() -> None:
    db = SessionLocal()
    try:
        seed_roles(db)
        seed_hackathon_and_problems(db)
        db.commit()
        print(f"[seed] completed at {datetime.now(timezone.utc).isoformat()}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
