import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Problem, ProblemTest


class ProblemRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, problem_id: uuid.UUID) -> Problem | None:
        return self.db.get(Problem, problem_id)

    def list_problems(
        self, *, hackathon_id: uuid.UUID | None, page: int, page_size: int
    ) -> tuple[list[Problem], int]:
        stmt = select(Problem)
        count_stmt = select(func.count()).select_from(Problem)

        if hackathon_id is not None:
            stmt = stmt.where(Problem.hackathon_id == hackathon_id)
            count_stmt = count_stmt.where(Problem.hackathon_id == hackathon_id)

        total = self.db.execute(count_stmt).scalar_one()
        stmt = stmt.order_by(Problem.order_index.asc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def create_problem(self, **fields) -> Problem:
        problem = Problem(**fields)
        self.db.add(problem)
        self.db.flush()
        return problem

    def delete_problem(self, problem: Problem) -> None:
        self.db.delete(problem)

    def get_test_by_id(self, test_id: uuid.UUID) -> ProblemTest | None:
        return self.db.get(ProblemTest, test_id)

    def list_tests_for_problem(self, problem_id: uuid.UUID) -> list[ProblemTest]:
        stmt = select(ProblemTest).where(ProblemTest.problem_id == problem_id)
        return list(self.db.execute(stmt).scalars().all())

    def create_test(self, problem_id: uuid.UUID, **fields) -> ProblemTest:
        test = ProblemTest(problem_id=problem_id, **fields)
        self.db.add(test)
        self.db.flush()
        return test

    def delete_test(self, test: ProblemTest) -> None:
        self.db.delete(test)

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, instance) -> None:
        self.db.refresh(instance)
