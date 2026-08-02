from pydantic import BaseModel


class TestCaseCreate(BaseModel):
    problem_id: int
    input_data: str
    expected_output: str
    is_hidden: bool = False


class TestCaseResponse(TestCaseCreate):
    id: int

    class Config:
        from_attributes = True
