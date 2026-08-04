from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from functools import lru_cache


class ChunkingService:

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                " ",
                ""
            ]
        )

    def chunk_text(self, text: str) -> list[str]:
        """
        Split a single document into chunks.
        """
        return self.splitter.split_text(text)

    def chunk_documents(self, documents: list[Document]) -> list[Document]:
        """
        Split multiple documents into chunks.
        """
        return self.splitter.split_documents(documents)


@lru_cache
def get_chunking_service():
    return ChunkingService()
