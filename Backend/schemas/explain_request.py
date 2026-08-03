from pydantic import BaseModel


class ExplainRequest(BaseModel):
    user_prompt: str
    source_code: str