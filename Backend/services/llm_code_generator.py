from services.llm_service import LLMService
from services.prompt_builder import PromptBuilderService
from schemas.retrieval_schema import RetrievedDocument 
from schemas.generation_response import CodeGenerationResponse
from services.memory_service import MemoryService
from langchain_core.messages import BaseMessage


class LLMCodeGenerator:
    def __init__(self, llm: LLMService, prompt_builder: PromptBuilderService,memory: MemoryService):
        self.llm = llm
        self.prompt_builder = prompt_builder
        self.memory = memory
    SYSTEM_PROMPT = """
You are an expert Python software engineer.

You are provided with one or more retrieved programming examples.

Use these examples only as references to understand the user's problem.

Rules:
- Do not copy the retrieved examples verbatim unless they exactly solve the user's request.
- Reuse ideas, algorithms, and implementation patterns when appropriate.
- Generate a complete and correct implementation.
- Return only the source code.
- Do not explain the solution.
- Do not use Markdown.
- Ensure the code is executable.
"""
    def generate_code(self, user_prompt: str, relevant_documents: list[RetrievedDocument], conversation_history: list[BaseMessage]) -> CodeGenerationResponse:
        prompt = self.prompt_builder.build_generation_prompt(
            user_prompt=user_prompt,
            relevant_documents=relevant_documents,
            conversation_history=conversation_history
        )

        response = self.llm.generate(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=prompt,
            temperature=0.7,
            max_tokens=1024,
        )
        return CodeGenerationResponse(
            language="python",
            code=response.strip(),
        )
            