from datasets import load_dataset
from langchain_core.documents import Document


class HumanEvalLoader:

    def load(self) -> list[Document]:
        """
        Load the HumanEval dataset and convert each sample
        into a LangChain Document.
        """

        dataset = load_dataset(
            "openai/openai_humaneval",
            split="test"
        )

        documents = []

        for sample in dataset:

            content = f"""
Problem:
{sample["prompt"]}

Reference Solution:
{sample["canonical_solution"]}
""".strip()

            metadata = {
                "task_id": sample["task_id"],
                "entry_point": sample["entry_point"],
                "source": "HumanEval",
                "language": "python",
            }

            documents.append(
                Document(
                    page_content=content,
                    metadata=metadata,
                )
            )

        return documents