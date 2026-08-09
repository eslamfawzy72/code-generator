from functools import lru_cache

from schemas.retrieval_schema import RetrievedDocument


class PromptBuilderService:

    def build_generation_prompt(
        self,
        user_prompt: str,
        relevant_documents: list[RetrievedDocument],
        conversation_history: list[str]
    ) -> str:

        context = []

        for index, document in enumerate(relevant_documents, start=1):
            context.append(
                f"""
    Example {index}

    Source: {document.metadata.get("source")}
    Language: {document.metadata.get("language")}

    {document.content}
    """
            )

        context_text = "\n".join(context)

        return f"""
        ========================
        Conversation History
        ========================
        {conversation_history}

        ========================
        Current User Request
        ========================
        {user_prompt}

        ========================
        Retrieved Programming Examples
        ========================
        {context_text}

        Generate the best solution using the conversation history when the request is a follow-up. Use the retrieved examples only as references.
        """

@lru_cache
def get_prompt_builder_service():
    return PromptBuilderService()