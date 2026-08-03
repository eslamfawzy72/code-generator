from pydantic import BaseModel


class LineExplanation(BaseModel):
    line_number: int
    line: str
    explanation: str
