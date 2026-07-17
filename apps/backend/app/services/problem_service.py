import uuid

from sqlalchemy.orm import Session

from app.repositories.problem_repository import ProblemRepository
from app.schemas.problem import (
    ProblemCreateRequest,
    ProblemTestCreateRequest,
    ProblemTestUpdateRequest,
    ProblemUpdateRequest,
)


class ProblemNotFoundError(Exception):
    pass


class ProblemTestNotFoundError(Exception):
    pass


class ProblemService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ProblemRepository(db)

    def create_problem(self, payload: ProblemCreateRequest):
        problem = self.repo.create_problem(
            hackathon_id=payload.hackathon_id,
            title=payload.title,
            description=payload.description,
            max_score=payload.max_score,
            order_index=payload.order_index,
        )
        self.repo.commit()
        self.repo.refresh(problem)
        return problem

    def list_problems(self, *, hackathon_id: uuid.UUID | None, page: int, page_size: int):
        return self.repo.list_problems(hackathon_id=hackathon_id, page=page, page_size=page_size)

    def get_problem(self, problem_id: uuid.UUID):
        problem = self.repo.get_by_id(problem_id)
        if problem is None:
            raise ProblemNotFoundError()
        return problem

    def update_problem(self, problem_id: uuid.UUID, payload: ProblemUpdateRequest):
        problem = self.repo.get_by_id(problem_id)
        if problem is None:
            raise ProblemNotFoundError()

        for field in ("title", "description", "max_score", "order_index"):
            value = getattr(payload, field)
            if value is not None:
                setattr(problem, field, value)

        self.repo.commit()
        self.repo.refresh(problem)
        return problem

    def delete_problem(self, problem_id: uuid.UUID) -> None:
        problem = self.repo.get_by_id(problem_id)
        if problem is None:
            raise ProblemNotFoundError()
        self.repo.delete_problem(problem)
        self.repo.commit()

    def add_test(self, problem_id: uuid.UUID, payload: ProblemTestCreateRequest):
        problem = self.repo.get_by_id(problem_id)
        if problem is None:
            raise ProblemNotFoundError()

        test = self.repo.create_test(
            problem_id=problem_id,
            input_data=payload.input_data,
            expected_output=payload.expected_output,
            is_hidden=payload.is_hidden,
            weight=payload.weight,
        )
        self.repo.commit()
        self.repo.refresh(test)
        return test

    def list_tests(self, problem_id: uuid.UUID):
        if self.repo.get_by_id(problem_id) is None:
            raise ProblemNotFoundError()
        return self.repo.list_tests_for_problem(problem_id)

    def update_test(self, problem_id: uuid.UUID, test_id: uuid.UUID, payload: ProblemTestUpdateRequest):
        test = self.repo.get_test_by_id(test_id)
        if test is None or test.problem_id != problem_id:
            raise ProblemTestNotFoundError()

        for field in ("input_data", "expected_output", "is_hidden", "weight"):
            value = getattr(payload, field)
            if value is not None:
                setattr(test, field, value)

        self.repo.commit()
        self.repo.refresh(test)
        return test

    def delete_test(self, problem_id: uuid.UUID, test_id: uuid.UUID) -> None:
        test = self.repo.get_test_by_id(test_id)
        if test is None or test.problem_id != problem_id:
            raise ProblemTestNotFoundError()
        self.repo.delete_test(test)
        self.repo.commit()
