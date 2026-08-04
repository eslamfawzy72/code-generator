from pathlib import Path
import sys


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from loaders.humaneval_loader import HumanEvalLoader
from services.ingestion_service import get_ingestion_service


class PopulateDB:

    def populate(self):
        """
        Populate the database with the HumanEval dataset.
        """

        loader = HumanEvalLoader()
        documents = loader.load()

        ingestion_service = get_ingestion_service()
        ingestion_service.ingest_documents(documents)

        print(f"Inserted {len(documents)} documents into ChromaDB.")


def main() -> None:
    PopulateDB().populate()


if __name__ == "__main__":
    main()
