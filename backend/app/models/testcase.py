from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey
)

from app.database import Base


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    problem_id = Column(
        Integer,
        ForeignKey("problems.id")
    )

    input_data = Column(
        String,
        nullable=False
    )

    expected_output = Column(
        String,
        nullable=False
    )

    is_hidden = Column(
        Boolean,
        default=False
    )
