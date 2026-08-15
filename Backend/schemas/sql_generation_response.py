from pydantic import BaseModel
from typing import Literal


class SQLGenerationResponse(BaseModel):
    status: Literal["success", "error"]
    sql: str | None = None
    error: str | None = None