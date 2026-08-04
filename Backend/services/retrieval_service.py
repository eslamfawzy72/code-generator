from functools import lru_cache

from langchain_core.documents import Document

from clients.chroma_client import get_chroma_client
from services.embedding_service import get_embedding_service


class RetrievalService:

    def __init__(self):
        self.chroma_client = get_chroma_client()
        self.embedding_service = get_embedding_service()

    def retrieve(
        self,
        query: str,
        k: int = 3,
    ) -> list[Document]:
        """
        Retrieve the top-k most relevant documents from Chroma.
        """

        query_embedding = self.embedding_service.embed_query(query)

        collection = self.chroma_client.get_collection()

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
        )

        documents = []

        retrieved_docs = results.get("documents", [[]])[0]
        retrieved_metadata = results.get("metadatas", [[]])[0]

        for content, metadata in zip(
            retrieved_docs,
            retrieved_metadata,
        ):
            documents.append(
                Document(
                    page_content=content,
                    metadata=metadata,
                )
            )

        return documents


@lru_cache
def get_retrieval_service():
    return RetrievalService()