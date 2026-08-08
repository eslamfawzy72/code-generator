from functools import lru_cache

from services import retrieval_service
from services.llm_service import LLMService
from services.llm_classifier import Intent, LLMClassifier
from services.llm_explainer import LLMExplainer
from services.memory_service import MemoryService
from services.code_execution_service import ExecutionService
from services.prompt_builder import PromptBuilderService
from services.llm_code_generator import LLMCodeGenerator
from dto.intents import Intent
from schemas.response_schema import BaseResponse
from services.code_execution_service import ExecutionService
from schemas.generation_response import CodeGenerationResponse
from schemas.explain_response import ExplainResponse
from schemas.execution_response import ExecutionResponse
from schemas.generate_path_response import GenerateResponse
from services.relevance_checker_service import RelevanceCheckerService
from services.retrieval_service import RetrievalService

class OrchestratorService:
    def __init__(self, classifier: LLMClassifier, explainer: LLMExplainer, memory_service: MemoryService,
                 execution_service: ExecutionService,
                 code_generator: LLMCodeGenerator,
                 relevence_service: RelevanceCheckerService,
                 retrieval_service: RetrievalService
                 ):
        self.classifier = classifier
        self.explainer = explainer
        self.memory_service = memory_service
        self.execution_service = execution_service
        self.code_generator = code_generator
        self.relevance_service = relevence_service
        self.retrieval_service = retrieval_service

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
        if intent == Intent.GENERATE.value:
            retrieval_response = self.retrieval_service.retrieve(user_prompt)

            relevance_response = self.relevance_service.check(
                query=user_prompt,
                retrieved_documents=retrieval_response,
            )

            relevant_documents = [
                retrieval_response.documents[result.document_index]
                for result in relevance_response.results
                if result.relevant
            ]

            generation = self.code_generator.generate_code(
                user_prompt=user_prompt,
                relevant_documents=relevant_documents,
            )

            execution = self.execution_service.execute(generation)

            self.memory_service.add_ai_message(generation.code)

            return GenerateResponse(
                generation=generation,
                execution=execution,
            )
        
    @lru_cache(maxsize=1)    
    def get_orchestrator_service():
        classifier_llm = LLMService("qwen2.5:3b")
        explainer_llm = LLMService("qwen2.5:3b")
        memory_service = MemoryService()
        execution_service = ExecutionService()
        generator_llm = LLMService("qwen2.5:3b")
        relevance_llm = LLMService("qwen2.5:3b")
        prompt_builder = PromptBuilderService()
        code_generator = LLMCodeGenerator(generator_llm, prompt_builder)
        classifier = LLMClassifier(classifier_llm)
        explainer = LLMExplainer(explainer_llm)
        relevance_service = RelevanceCheckerService(relevance_llm)
        retrieval_service = RetrievalService()
        
        return OrchestratorService(
            classifier=classifier,
            explainer=explainer,
            memory_service=memory_service,
            execution_service=execution_service,
            code_generator=code_generator,
            relevence_service=relevance_service,
            retrieval_service=retrieval_service
        )
    