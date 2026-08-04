import chromadb
from functools import lru_cache

from sympy import limit

from core.config import settings


class ChromaClient:

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PATH
        )

        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION
        )

    def get_collection(self):
        return self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION
        )

    def reset_collection(self):
        self.client.delete_collection(settings.CHROMA_COLLECTION)

        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION
        )
    def count(self):
        return self.get_collection().count()
    def peek(self, limit: int = 5):
        return self.get_collection().peek(limit=limit)

@lru_cache
def get_chroma_client():
    return ChromaClient()
