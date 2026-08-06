from services.retrieval_service import get_retrieval_service
from services.relevance_checker_service import get_relevance_checker_service

retriever = get_retrieval_service()
relevance_checker = get_relevance_checker_service()

query = "Write a function that checks if two numbers are close."

retrieval_response = retriever.retrieve(query)

print("=" * 60)
print(f"Retrieved {len(retrieval_response.documents)} documents")
print("=" * 60)

for i, document in enumerate(retrieval_response.documents):
    print(f"\nDocument {i}")
    print("-" * 60)
    print(document.metadata)
    print()
    print(document.content[:500])

print("\n")
print("=" * 60)
print("Running Relevance Checker...")
print("=" * 60)

relevance_response = relevance_checker.check(
    query=query,
    retrieved_documents=retrieval_response,
)

print("\nRelevance Result:\n")

print(f"Has Relevant Documents: {relevance_response.has_relevant_documents}")
for result in relevance_response.results:
    print(f"Document {result.document_index}")
    print(f"Relevant : {result.relevant}")
    print(f"Reason   : {result.reason}")
    print("-" * 60)