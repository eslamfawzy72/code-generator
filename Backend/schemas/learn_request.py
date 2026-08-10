from pydantic import BaseModel, Field


class LearnRequest(BaseModel):
    problem: str = Field(
        ...,
        description="The original programming problem.",
    )