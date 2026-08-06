from functools import lru_cache

import json
from services.llm_service import LLMService
from schemas.retrieval_schema import RetrievalResponse
from schemas.relevance_response import RelevanceResponse


class RelevanceCheckerService:
    def __init__(self, llm: LLMService):
        self.llm_service = llm
    SYSTEM_PROMPT = """
    You are an expert retrieval evaluator.

    Your task is to determine whether each retrieved document is useful
    for answering the user's request.

    For every retrieved document:

    - Decide whether it is relevant.
    - Give a short reason.

    Return ONLY valid JSON.

    Schema:

    {
        
        "results": [
            {
                "document_index": 0,
                "relevant": true,
                "reason": "..."
            }
        ]
    }
    """
    

    def _parse_response(self, response: str) -> dict:
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            start = response.find("{")
            end = response.rfind("}")
            if start != -1 and end != -1 and start < end:
                return json.loads(response[start:end + 1])
            raise ValueError("LLM returned invalid JSON")
    def prompt_builder(
        self,
        query: str,
        retrieved_documents: RetrievalResponse,
    ) -> str:

        documents = []

        for index, document in enumerate(retrieved_documents.documents):
            documents.append(
                f"""
    Document {index}

    Content:
    {document.content}
    """
            )

        documents_text = "\n".join(documents)

        return f"""
    User Request:
    {query}

    Retrieved Documents:

    {documents_text}
    """
    def check(
        self,
        query: str,
        retrieved_documents: RetrievalResponse,
    ) -> RelevanceResponse:

        prompt = self.prompt_builder(
            query=query,
            retrieved_documents=retrieved_documents,
        )

        generation_options = {
            "system_prompt": self.SYSTEM_PROMPT,
            "user_prompt": prompt,
            "temperature": 0,
            "max_tokens": 512,
            "response_format": "json",
        }

        response = self.llm_service.generate(**generation_options)
        data = self._parse_response(response)
        relevance_response = RelevanceResponse.model_validate(data)
        relevance_response.has_relevant_documents = any(
        result.relevant
        for result in relevance_response.results
        )
        return relevance_response
    
@lru_cache
def get_relevance_checker_service():
    return RelevanceCheckerService(llm=LLMService.get_llm_service())