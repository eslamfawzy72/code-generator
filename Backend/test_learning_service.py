from services.learning_service import get_learning_service
from services.retrieval_service import get_retrieval_service
from services.relevance_checker_service import get_relevance_checker_service
from services.llm_code_generator import LLMCodeGenerator
from services.llm_service import LLMService
from services.prompt_builder import get_prompt_builder_service

retriever = get_retrieval_service()
relevance_checker = get_relevance_checker_service()
learning_service = get_learning_service()

code_generator = LLMCodeGenerator(
    llm=LLMService.get_llm_service(),
    prompt_builder=get_prompt_builder_service(),
)

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

# ==========================================================
# Code Generation Path
# ==========================================================
if relevance_response.has_relevant_documents:

    print("\nGenerating code...\n")

    relevant_documents = [
        retrieval_response.documents[result.document_index]
        for result in relevance_response.results
        if result.relevant
    ]

    generated_code = code_generator.generate_code(
        user_prompt=query,
        relevant_documents=relevant_documents,
    )

    print("=" * 60)
    print("Generated Code")
    print("=" * 60)
    print(generated_code.code)

# ==========================================================
# Learning Path
# ==========================================================
else:

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