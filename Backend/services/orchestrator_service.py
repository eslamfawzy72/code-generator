from functools import lru_cache
from services.llm_service import LLMService
from services.llm_classifier import LLMClassifier
from services.llm_explainer import LLMExplainer
from services.memory_service import MemoryService
from services.prompt_builder import PromptBuilderService
from services.llm_code_generator import LLMCodeGenerator
from dto.intents import Intent
from schemas.response_schema import BaseResponse
from services.code_execution_service import ExecutionService
from services.llm_code_extraction_service import LLMCodeExtractor
from schemas.generate_path_response import GenerateResponse
from schemas.learning_required_response import LearningRequiredResponse
from services.relevance_checker_service import RelevanceCheckerService
from services.retrieval_service import RetrievalService
from services.learning_service import LearningService

class OrchestratorService:
    def __init__(self, classifier: LLMClassifier, explainer: LLMExplainer, memory_service: MemoryService,
                 execution_service: ExecutionService,
                 code_generator: LLMCodeGenerator,
                 relevence_service: RelevanceCheckerService,
                 retrieval_service: RetrievalService,
                 extraction_service: LLMCodeExtractor,
                 learning_service: LearningService,
                 ):
        self.classifier = classifier
        self.explainer = explainer
        self.memory_service = memory_service
        self.execution_service = execution_service
        self.code_generator = code_generator
        self.relevance_service = relevence_service
        self.retrieval_service = retrieval_service
        self.extractor_service = extraction_service
        self.learning_service = learning_service
        
    def _classify_intent(self, user_prompt: str) -> str:
        intent = self.classifier.classify(user_prompt)
        return intent.value
    
    def handle_request(self, user_prompt: str) -> BaseResponse:
        intent = self._classify_intent(user_prompt)
        if intent == Intent.EXPLAIN.value:

            extraction = self.extractor_service.extract(user_message=user_prompt)

            if extraction.code_found:
                source_code = extraction.source_code
                self.memory_service.set_current_source_code(source_code)
            else:
                source_code = self.memory_service.get_current_source_code()

        

            history = self.memory_service.get_history()

            response = self.explainer.explain(
                user_prompt=user_prompt,
                conversation_history=history,
                source_code=source_code,
            )

            self.memory_service.add_user_message(user_prompt)

            assistant_message = response.summary

            for line in response.lines:
                assistant_message += (
                    f"\nLine {line.line_number}: {line.explanation}"
                )

            self.memory_service.add_ai_message(assistant_message)

            return response
        if intent == Intent.GENERATE.value:
            self.memory_service.add_user_message(user_prompt)

            history = self.memory_service.get_history()
            retrieval_response = self.retrieval_service.retrieve(user_prompt)

            relevance_response = self.relevance_service.check(
                query=user_prompt,
                retrieved_documents=retrieval_response,
            )

            if not relevance_response.has_relevant_documents:
                learning_response = LearningRequiredResponse(
                    message=(
                        "I couldn't solve this problem because I don't have a "
                        "similar example. Please upload the correct Python solution so I can learn it."
                    )
                )

                self.memory_service.add_ai_message(learning_response.message)

                return learning_response

            relevant_documents = [
                retrieval_response.documents[result.document_index]
                for result in relevance_response.results
                if result.relevant
            ]

            generation = self.code_generator.generate_code(
                user_prompt=user_prompt,
                relevant_documents=relevant_documents,
                conversation_history=history
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
        code_generator = LLMCodeGenerator(generator_llm, prompt_builder, memory_service)
        classifier = LLMClassifier(classifier_llm)
        explainer = LLMExplainer(explainer_llm)
        relevance_service = RelevanceCheckerService(relevance_llm)
        retrieval_service = RetrievalService()
        learning_service = LearningService()
        extraction_llm = LLMService("qwen2.5:3b")
        extraction_service = LLMCodeExtractor(extraction_llm)
        
        return OrchestratorService(
            classifier=classifier,
            explainer=explainer,
            memory_service=memory_service,
            execution_service=execution_service,
            code_generator=code_generator,
            relevence_service=relevance_service,
            retrieval_service=retrieval_service,
            extraction_service=extraction_service,
            learning_service=learning_service,
        )
    