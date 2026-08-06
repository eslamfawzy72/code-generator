from services.learning_service import get_learning_service
from services.retrieval_service import get_retrieval_service
from services.relevance_checker_service import get_relevance_checker_service

retriever = get_retrieval_service()
relevance_checker = get_relevance_checker_service()
learning_service = get_learning_service()

query = input("Enter your programming problem:\n> ")

retrieval_response = retriever.retrieve(query)

print("=" * 60)
print(f"Retrieved {len(retrieval_response.documents)} documents")
print("=" * 60)

for i, document in enumerate(retrieval_response.documents):
    print(f"\nDocument {i}")
    print("-" * 60)
    print(document.metadata)
    print(document.content[:300])
    print()

print("\nRunning Relevance Checker...\n")

relevance_response = relevance_checker.check(
    query=query,
    retrieved_documents=retrieval_response,
)

print(f"Has Relevant Documents: {relevance_response.has_relevant_documents}\n")

for result in relevance_response.results:
    print(f"Document {result.document_index}")
    print(f"Relevant : {result.relevant}")
    print(f"Reason   : {result.reason}")
    print("-" * 60)

# -----------------------------
# Learning path
# -----------------------------
flag=False
for i in range(len(relevance_response.results)):
    if relevance_response.results[i].relevant==True:
        flag=True
        break
if not flag:

    print("\nNo relevant documents were found.")
    print("Please provide the path to a Python file containing the correct solution.")

    solution_path = input("\nSolution file (.py): ").strip()

    try:
        with open(solution_path, "r", encoding="utf-8") as file:
            solution = file.read()

        learning_service.learn(
            problem=query,
            solution=solution,
            language="python",
        )

        print("\n✅ Solution successfully stored in the vector database!")

    except FileNotFoundError:
        print(f"\n❌ File not found: {solution_path}")

    except Exception as e:
        print(f"\n❌ Failed to store solution: {e}")

else:
    print("\nProceed to the code generation pipeline.")