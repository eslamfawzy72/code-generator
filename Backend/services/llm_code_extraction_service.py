from functools import lru_cache
import json

from schemas.code_extraction_response import CodeExtractionResponse
from services.llm_service import LLMService


class LLMCodeExtractor:

    SYSTEM_PROMPT = """
You are an expert programming assistant.

Your task is to separate a user's message into:

1. The actual programming question.
2. The source code (if any).

Rules:

- The source code may be written in ANY programming language.
- The source code may or may not be inside markdown code blocks.
- Users may simply paste code without using ```.

If source code exists:
- Extract it exactly.
- Preserve indentation.
- Do not modify formatting.
- Do not fix syntax errors.

The user_prompt should contain only the natural language request.

If no source code exists:
- source_code must be an empty string.

Return ONLY valid JSON.

Schema:

{
    "user_prompt": "...",
    "source_code": "...",
    "code_found": true/false
}
"""

    def __init__(self, llm: LLMService):
        self.llm = llm

    def _parse_response(self, response: str) -> dict:

        try:
            return json.loads(response)

        except json.JSONDecodeError:

            start = response.find("{")
            end = response.rfind("}")

            if start != -1 and end != -1:
                return json.loads(response[start:end + 1])

            raise ValueError("Invalid JSON returned by LLM")

    def extract(
        self,
        user_message: str,
    ) -> CodeExtractionResponse:

        response = self.llm.generate(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_message,
            temperature=0,
            response_format="json",
            max_tokens=1024,
        )

        data = self._parse_response(response)

        return CodeExtractionResponse.model_validate(data)


@lru_cache
def get_code_extractor_service():
    return LLMCodeExtractor(
        LLMService("qwen2.5:3b")
    )