import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from runner.db import ExecutionResult, Problem, ProblemTest, Score, Submission, SubmissionStatus
from runner.scoring_client import trigger_scoring
from sandbox.docker_runner import SandboxRunner
from utils.scoring import compute_score

logger = logging.getLogger("aeos.executor")


class SubmissionProcessor:
    def __init__(self, db: Session, sandbox: SandboxRunner | None = None) -> None:
        self.db = db
        self.sandbox = sandbox or SandboxRunner()

    def process(self, submission_id: str) -> None:
        submission = self.db.get(Submission, uuid.UUID(submission_id))
        if submission is None:
            logger.error("Submission %s not found; skipping", submission_id)
            return

        submission.status = SubmissionStatus.RUNNING
        self.db.commit()

        try:
            problem = self.db.get(Problem, submission.problem_id)
            tests = list(
                self.db.execute(
                    select(ProblemTest).where(ProblemTest.problem_id == submission.problem_id)
                )
                .scalars()
                .all()
            )

            if not tests:
                logger.warning("Problem %s has no test cases", submission.problem_id)

            passed_flags: list[bool] = []
            weights: list[float] = []

            for test in tests:
                outcome = self.sandbox.run(submission.language, submission.code, test.input_data)

                actual_output = outcome.stdout.strip()
                expected_output = test.expected_output.strip()
                passed = (
                    not outcome.timed_out
                    and outcome.exit_code == 0
                    and actual_output == expected_output
                )

                error_message = None
                if outcome.timed_out:
                    error_message = "Execution timed out"
                elif outcome.exit_code not in (0, None) or outcome.stderr.strip():
                    error_message = outcome.stderr.strip()[:2000] or None

                self.db.add(
                    ExecutionResult(
                        submission_id=submission.id,
                        problem_test_id=test.id,
                        passed=passed,
                        actual_output=actual_output[:5000],
                        execution_time_ms=outcome.execution_time_ms,
                        error_message=error_message,
                    )
                )

                passed_flags.append(passed)
                weights.append(test.weight)

            points = compute_score(problem.max_score, weights, passed_flags) if problem else 0.0

            existing_score = self.db.execute(
                select(Score).where(Score.submission_id == submission.id)
            ).scalar_one_or_none()
            if existing_score is None:
                self.db.add(
                    Score(
                        submission_id=submission.id,
                        user_id=submission.user_id,
                        problem_id=submission.problem_id,
                        points=points,
                        max_points=float(problem.max_score) if problem else 0.0,
                    )
                )
            else:
                existing_score.points = points

            submission.status = SubmissionStatus.COMPLETED
            self.db.commit()

            trigger_scoring(str(submission.id))

        except Exception:
            logger.exception("Execution failed for submission %s", submission_id)
            self.db.rollback()
            submission.status = SubmissionStatus.FAILED
            self.db.commit()
