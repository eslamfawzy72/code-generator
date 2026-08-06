from functools import lru_cache

from schemas.retrieval_schema import RetrievedDocument


class PromptBuilderService:

    def build_generation_prompt(
        self,
        user_prompt: str,
        relevant_documents: list[RetrievedDocument],
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
    User Request:
    {user_prompt}

    Retrieved Examples:
    {context_text}
    """

@lru_cache
def get_prompt_builder_service():
    return PromptBuilderService()