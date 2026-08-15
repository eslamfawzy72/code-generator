from pydantic import BaseModel


class SpeechResponse(BaseModel):
    status: str
    text: str | None = None
    language: str | None = None
    error: str | None = None