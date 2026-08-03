from enum import Enum
from functools import lru_cache

# from langchain_core.prompts import PromptTemplate
from services.llm_service import LLMService
from dto.intents import Intent



class LLMClassifier:
    
    SYSTEM_PROMPT ="""
    You are an intent classifier.

Your task is to classify a programming request.

Possible labels:

EXPLAIN
- User wants an explanation of existing code.
- User asks what code does.
- User asks why code behaves in a certain way.
- User asks to explain code line by line.
- User asks to debug or analyze existing code.

GENERATE
- User asks to write code.
- User asks to implement something.
- User asks to build an API, model, algorithm, project, or function.
- User asks for sample code.

Rules:
- Return ONLY one word.
- Either EXPLAIN or GENERATE.
- Do not explain your decision.
    """
    
    def __init__(self, llm: LLMService):
        self.llm=llm
        
    def classify(self, user_prompt:str)->Intent:
        prompt =f"""
        user request: {user_prompt}
        """
        response =self.llm.generate(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=prompt,
            temperature=0,
            max_tokens=128
        ).strip().upper()
        try:
            return Intent(response)
        except ValueError:
            raise ValueError(f"Invalid intent: {response}")
    @lru_cache
    def get_classifier_llm():
        return LLMService("qwen2.5:3b")

        