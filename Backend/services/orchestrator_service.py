from functools import lru_cache

from services.llm_service import LLMService
from services.llm_classifier import Intent, LLMClassifier
from services.llm_explainer import LLMExplainer
from services.memory_service import MemoryService
from dto.intents import Intent
from schemas.response_schema import BaseResponse

class OrchestratorService:
    def __init__(self, classifier: LLMClassifier, explainer: LLMExplainer, memory_service: MemoryService):
        self.classifier = classifier
        self.explainer = explainer
        self.memory_service = memory_service
        
    def _classify_intent(self, user_prompt: str) -> str:
        intent = self.classifier.classify(user_prompt)
        return intent.value
    
    def handle_request(self, user_prompt: str, source_code: str) -> BaseResponse:
        intent = self._classify_intent(user_prompt)
        if intent == Intent.EXPLAIN.value:
            
            self.memory_service.add_user_message(user_prompt)
            history = self.memory_service.get_history()
            response = self.explainer.explain(
                user_prompt=user_prompt,
                conversation_history=history,
                source_code=source_code,
            )
            self.memory_service.add_ai_message(response.summary)
            return response
        
    @lru_cache(maxsize=1)    
    def get_orchestrator_service():
        classifier_llm = LLMService("qwen2.5:3b")
        explainer_llm = LLMService("qwen2.5:3b")
        memory_service = MemoryService()
        
        classifier = LLMClassifier(classifier_llm)
        explainer = LLMExplainer(explainer_llm)
        
        return OrchestratorService(
            classifier=classifier,
            explainer=explainer,
            memory_service=memory_service
        )
    