from pydantic import BaseModel


class ProblemCreate(BaseModel):
    title: str
    description: str
    difficulty: str
    points: int


class ProblemResponse(
    ProblemCreate
):
    id: int

    class Config:
        from_attributes = True
