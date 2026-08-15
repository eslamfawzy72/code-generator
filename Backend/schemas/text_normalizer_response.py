from pydantic import BaseModel


class TextNormalizationResponse(BaseModel):
    status: str
    text: str | None = None
    error: str | None = None