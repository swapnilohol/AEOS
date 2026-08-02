from pydantic import BaseModel


class SubmissionCreate(
    BaseModel
):
    problem_id: int
    language: str
    source_code: str


class SubmissionResponse(
    BaseModel
):
    id: int
    status: str
    score: int

    class Config:
        from_attributes = True
