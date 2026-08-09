from pydantic import BaseModel, Field


class OrchestratorRequest(BaseModel):
    user_prompt: str = Field(
        ...,
        description="The user's request."
    )

