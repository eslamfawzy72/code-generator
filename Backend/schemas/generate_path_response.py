

from schemas.response_schema import BaseResponse
from schemas.execution_response import ExecutionResponse
from schemas.generation_response import CodeGenerationResponse

class GenerateResponse(BaseResponse):
    generation: CodeGenerationResponse
    execution: ExecutionResponse