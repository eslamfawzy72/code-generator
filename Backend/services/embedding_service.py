from functools import lru_cache

from ollama import embed

from core.config import settings


class EmbeddingService:

    MODEL_NAME = settings.OLLAMA_EMBEDDING_MODEL

    def _embed(self, texts: list[str]) -> list[list[float]]:
        response = embed(
            model=self.MODEL_NAME,
            input=texts,
        )
        return response["embeddings"]

    def embed_query(self, text: str) -> list[float]:
        """
        Generate an embedding for a single query.
        """
        return self._embed([text])[0]

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        embeddings = []
        batch_size = 8

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]

            print(f"Embedding batch {i // batch_size + 1} ({len(batch)} docs)...")

            batch_embeddings = self._embed(batch)

            embeddings.extend(batch_embeddings)

        return embeddings


@lru_cache
def get_embedding_service():
    return EmbeddingService()
