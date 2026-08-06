import re
import uuid
from functools import lru_cache

from clients.chroma_client import get_chroma_client
from services.embedding_service import get_embedding_service


class LearningService:

    def __init__(self):
        self.chroma_client = get_chroma_client()
        self.embedding_service = get_embedding_service()

    def learn(
        self,
        problem: str,
        solution: str,
        language: str = "python",
    ) -> None:
        """
        Learn a new programming example by storing it
        in the vector database.
        """

        task_id = self._generate_task_id()
        entry_point = self._extract_entry_point(solution)

        document = self._build_document(
            problem=problem,
            solution=solution,
        )

        embedding = self.embedding_service.embed_query(document)

        metadata = {
            "task_id": task_id,
            "source": "User",
            "language": language,
            "entry_point": entry_point,
        }

        collection = self.chroma_client.get_collection()

        collection.add(
            ids=[task_id],
            documents=[document],
            embeddings=[embedding],
            metadatas=[metadata],
        )

    def _build_document(
        self,
        problem: str,
        solution: str,
    ) -> str:

        return f"""Problem:

{problem}

Reference Solution:

{solution}
"""

    def _extract_entry_point(
        self,
        solution: str,
    ) -> str:
        """
        Extract the function name from a Python solution.
        """

        match = re.search(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", solution)

        if match:
            return match.group(1)

        return "unknown"

    def _generate_task_id(self) -> str:
        return f"user_{uuid.uuid4().hex[:8]}"


@lru_cache
def get_learning_service():
    return LearningService()