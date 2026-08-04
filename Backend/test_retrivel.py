from services.retrieval_service import get_retrieval_service

retriever = get_retrieval_service()

documents = retriever.retrieve(
    "Write a function that checks if two numbers are close."
)

print(f"Retrieved {len(documents)} documents\n")

for i, doc in enumerate(documents, start=1):
    print("=" * 60)
    print(f"Document {i}")
    print(doc.metadata)
    print()
    print(doc.page_content[:500])
    print()