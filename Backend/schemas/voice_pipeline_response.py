from pydantic import BaseModel
from typing import Any


class VoicePipelineResponse(BaseModel):
    status: str
    transcription: str | None = None
    detected_language: str | None = None
    sql_query: str | None = None
    result: Any | None = None
    error: str | None = None