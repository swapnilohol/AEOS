from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    difficulty = Column(
        String,
        default="Easy"
    )

    points = Column(
        Integer,
        default=100
    )
