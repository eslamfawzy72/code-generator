from pydantic import BaseModel


class CodeExtractionResponse(BaseModel):
    user_prompt: str
    source_code: str
    code_found: bool