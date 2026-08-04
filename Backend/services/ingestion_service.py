from langchain_core.documents import Document
from functools import lru_cache
import uuid


from clients.chroma_client import get_chroma_client
from services.chunking_service import get_chunking_service
from services.embedding_service import get_embedding_service



class IngestionService:

    def __init__(self):
        self.collection = get_chroma_client().get_collection()
        self.chunking_service = get_chunking_service()
        self.embedding_service = get_embedding_service()

    def ingest_documents(
        self,
        documents: list[Document]
    ) -> None:

        chunks = self.chunking_service.chunk_documents(documents)

        texts = [
            chunk.page_content
            for chunk in chunks
        ]

        embeddings = self.embedding_service.embed_documents(texts)

        self.collection.add(
            ids=[str(uuid.uuid4()) for _ in range(len(chunks))],

            documents=texts,

            embeddings=embeddings,

            metadatas=[
                chunk.metadata
                for chunk in chunks
            ]
        )
        
@lru_cache
def get_ingestion_service():
    return IngestionService()

