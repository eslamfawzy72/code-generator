from functools import lru_cache
import json

from schemas.explain_response import ExplainResponse

from services.llm_classifier import LLMClassifier
from services.llm_service import LLMService
from dto.intents import Intent

class LLMExplainer:
    SYSTEM_PROMPT = """
    You are an expert software engineer and programming tutor.

Your task is to explain existing source code clearly and accurately.

Responsibilities:
- Explain what the code does.
- Explain the purpose of functions, classes, and variables.
- Describe the control flow and logic.
- Explain algorithms and important programming concepts.
- Identify potential bugs, code smells, inefficiencies, or bad practices when applicable.
- Explain errors if the user asks about them.
- If requested, explain the code line by line.

Rules:
- Never generate a completely new implementation unless the user explicitly asks for one.
- Focus on explaining the provided code instead of rewriting it.
- Be concise but complete.
- Use Markdown formatting.
- When referring to code, use Markdown code blocks.
- If the user provides incomplete code, explain only what can be inferred and clearly mention any missing context.
- If the user asks a follow-up question, use the previous conversation context to provide a coherent explanation.
- If you are uncertain about any behavior because of missing code or dependencies, state your assumptions instead of guessing.
 
When explaining code:

1. Give a short overview.
2. Explain important functions or classes.
3. explain the code line by line no omissions.
4. Mention potential issues or improvements if they exist.
5. Do not rewrite the entire implementation unless explicitly asked.  

Output Requirements:

Return ONLY valid JSON.

Do not use markdown.
Do not use ```json.
Do not include comments.
Do not include explanations.

Return exactly one JSON object.

The JSON must follow exactly this schema:

{
  "summary": "Short overview of the code.",
  "lines": [
    {
      "line_number": 1,
      "line": "code here",
      "explanation": "Explanation here"
    }
  ]
}

Rules:
- Do not wrap the JSON in markdown.
- Do not write any text before or after the JSON.
- Return valid JSON only.    
    
    """
    def __init__(self, llm: LLMService):
        self.llm = llm
        
        
    def prompt_builder(self, user_prompt:str, conversation_history:str, source_code:str)->str:
            return f"""
            User Request:
            {user_prompt}

            Conversation History:
            {conversation_history}

            Source Code:
            {source_code}
            """

       
        
     
    def _parse_response(self, response: str) -> dict:
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            start = response.find("{")
            end = response.rfind("}")
            if start != -1 and end != -1 and start < end:
                return json.loads(response[start : end + 1])
            raise ValueError("LLM returned invalid JSON")

    def explain(self, user_prompt:str, conversation_history:str="", source_code:str="")->ExplainResponse:
        prompt = self.prompt_builder(user_prompt=user_prompt,
                                     source_code=source_code,
                                     conversation_history=conversation_history)

        generation_options = {
            "system_prompt": self.SYSTEM_PROMPT,
            "user_prompt": prompt,
            "temperature": 0,
            "max_tokens": 1024,
            "response_format": "json",
        }

        response = self.llm.generate(**generation_options)
        try:
            data = self._parse_response(response)
        except ValueError:
            retry_prompt = f"{prompt}\n\nReturn the response again as one complete JSON object."
            retry_response = self.llm.generate(
                **{
                    **generation_options,
                    "user_prompt": retry_prompt,
                    "max_tokens": 1536,
                }
            )
            data = self._parse_response(retry_response)
        data["intent"] = Intent.EXPLAIN
        return ExplainResponse.model_validate(data)
    @lru_cache
    def get_explainer_llm():
        return LLMService("qwen2.5:3b")
