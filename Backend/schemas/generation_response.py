from schemas.response_schema import BaseResponse


class CodeGenerationResponse(BaseResponse):
    language: str
    code: str
    explanation: str | None = None