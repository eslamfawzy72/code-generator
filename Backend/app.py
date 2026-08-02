from services.llm_service import LLMService
from services.llm_classifier import LLMClassifier
from services.llm_explainer import LLMExplainer
from services.memory_service import MemoryService
from services.orchestrator import Orchestrator


def main():

    classifier_llm = LLMService(
        model_name="Qwen/Qwen2.5-3B-Instruct"
    )

    explainer_llm = LLMService(
        model_name="Qwen/Qwen2.5-3B-Instruct"
    )

    memory = MemoryService()

    classifier = LLMClassifier(classifier_llm)

    explainer = LLMExplainer(explainer_llm)

    orchestrator = Orchestrator(
        classifier=classifier,
        explainer=explainer,
        memory_service=memory,
    )

    while True:

        print("=" * 60)

        user_prompt = input("User: ")

        if user_prompt.lower() == "exit":
            break

        source_code = """
def find_max(numbers):
    if not numbers:
        return None

    maximum = numbers[0]

    for number in numbers:
        if number > maximum:
            maximum = number

    return maximum
"""

        response = orchestrator.handle_request(
            user_prompt=user_prompt,
            source_code=source_code,
        )

        print("\nAssistant:\n")
        print(response)
        print()


if __name__ == "__main__":
    main()