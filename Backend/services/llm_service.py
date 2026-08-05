from ollama import chat
from functools import lru_cache


class LLMService:

    def __init__(self, model_name: str = "qwen2.5:3b"):
        self.model_name = model_name

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0,
        max_tokens: int = 256,
        response_format: str | None = None,
    ) -> str:
        request_payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if response_format is not None:
            request_payload["format"] = response_format

        response = chat(**request_payload)

        return response["message"]["content"]
    
    @lru_cache
    def get_llm_service(model_name: str = "qwen2.5:3b") -> "LLMService":
        return LLMService(model_name)
