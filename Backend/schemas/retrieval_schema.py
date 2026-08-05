from pydantic import BaseModel
from typing import Any


class RetrievedDocument(BaseModel):
    content: str
    metadata: dict[str, Any]


class RetrievalResponse(BaseModel):
    documents: list[RetrievedDocument]