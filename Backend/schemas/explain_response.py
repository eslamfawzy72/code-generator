
from schemas.response_schema import BaseResponse
from schemas.line_explaination import LineExplanation

class ExplainResponse(BaseResponse):
    summary: str
    lines: list[LineExplanation]