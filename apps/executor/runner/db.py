"""
Minimal SQLAlchemy engine/session and model mirrors for the Executor
service.

NOTE ON DUPLICATION: apps/executor is a separate Docker build context from
apps/backend (see docker-compose.yml), so it cannot import apps/backend's
`app.models` package directly. Rather than restructure the whole repo to
share a Python package across two container images mid-hackathon (out of
scope for this module), the handful of columns the executor actually reads
or writes are mirrored here. This is documented tech debt — see
docs/README.md and the Architecture doc's "Future Scale Path" (a shared
`packages/shared` package is the natural fix later).

These models MUST stay schema-compatible with apps/backend/app/models; any
migration touching submissions, problems, problem_tests, execution_results,
or scores should be checked against this file too.
"""

import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text, create_engine, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from runner.config import settings


class Base(DeclarativeBase):
    pass


class SubmissionStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Problem(Base):
    __tablename__ = "problems"

    id = Column(UUID(as_uuid=True), primary_key=True)
    max_score = Column(Integer, nullable=False)


class ProblemTest(Base):
    __tablename__ = "problem_tests"

    id = Column(UUID(as_uuid=True), primary_key=True)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id"), nullable=False)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_hidden = Column(Boolean, nullable=False)
    weight = Column(Float, nullable=False)


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id"), nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    status = Column(Enum(SubmissionStatus, name="submission_status"), nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ExecutionResult(Base):
    __tablename__ = "execution_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False)
    problem_test_id = Column(UUID(as_uuid=True), ForeignKey("problem_tests.id"), nullable=False)
    passed = Column(Boolean, nullable=False)
    actual_output = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Score(Base):
    __tablename__ = "scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False, unique=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id"), nullable=False)
    points = Column(Float, nullable=False)
    max_points = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session() -> Session:
    return SessionLocal()
