from pydantic import BaseModel, Field


class OrchestratorRequest(BaseModel):
    user_prompt: str = Field(
        ...,
        description="The user's request."
    )

    source_code: str | None = Field(
        default=None,
        description="Optional source code used for explanation or other code-related tasks."
    )