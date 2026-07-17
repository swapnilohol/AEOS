import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ProblemCreateRequest(BaseModel):
    hackathon_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    max_score: int = Field(default=100, ge=1)
    order_index: int = Field(default=0, ge=0)


class ProblemUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    max_score: int | None = Field(default=None, ge=1)
    order_index: int | None = Field(default=None, ge=0)


class ProblemResponse(BaseModel):
    id: uuid.UUID
    hackathon_id: uuid.UUID
    title: str
    description: str
    max_score: int
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProblemListResponse(BaseModel):
    items: list[ProblemResponse]
    total: int
    page: int
    page_size: int


class ProblemTestCreateRequest(BaseModel):
    input_data: str = Field(min_length=1)
    expected_output: str = Field(min_length=1)
    is_hidden: bool = False
    weight: float = Field(default=1.0, gt=0)


class ProblemTestUpdateRequest(BaseModel):
    input_data: str | None = Field(default=None, min_length=1)
    expected_output: str | None = Field(default=None, min_length=1)
    is_hidden: bool | None = None
    weight: float | None = Field(default=None, gt=0)


class ProblemTestResponse(BaseModel):
    id: uuid.UUID
    problem_id: uuid.UUID
    input_data: str
    expected_output: str
    is_hidden: bool
    weight: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
