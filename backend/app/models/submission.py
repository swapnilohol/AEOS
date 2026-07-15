
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey
)

from app.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    problem_id = Column(
        Integer,
        ForeignKey("problems.id")
    )

    source_code = Column(Text)

    language = Column(
        String,
        default="python"
    )

    status = Column(
        String,
        default="PENDING"
    )

    output = Column(Text)

    score = Column(
        Integer,
        default=0
    )
