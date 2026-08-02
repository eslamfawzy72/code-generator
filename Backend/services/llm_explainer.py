from langchain_classic.prompts import PromptTemplate

from services.llm_classifier import LLMClassifier, Intent
from services.llm_service import LLMService
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
3. If requested, explain the code line by line.
4. Mention potential issues or improvements if they exist.
5. Do not rewrite the entire implementation unless explicitly asked.  
    
    
    """
    def __init__(self, llm: LLMService):
        self.llm = llm
        
        
    def prompt_builder(self, user_prompt:str, conversation_history:str, source_code:str)->str:
            template = PromptTemplate.from_template("""
            User Request:
            {user_request}

            Conversation History:
            {conversation_history}

            Source Code:
            {source_code}
            """)

            return template.format(
                user_request=user_prompt,
                conversation_history=conversation_history,
                source_code=source_code
            )
        
     
    def explain(self, user_prompt:str, conversation_history:str="", source_code:str="")->str:
        prompt = self.prompt_builder(user_prompt=user_prompt,
                                     source_code=source_code,
                                     conversation_history=conversation_history)
    
        return self.llm.generate(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=prompt,
            temperature=0,
            max_tokens=512
        )