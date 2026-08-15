from services.llm_service import LLMService
from services.sql_service import SQLiteService
from services.llm_query_generator import LLMQueryGenerator


def main():
    # Initialize services
    llm_service = LLMService(
        model_name="qwen2.5:3b",  # Update according to your configuration
    )

    sqlite_service = SQLiteService(
        db_path="database/data.db"  # Update path if needed
    )

    query_generator = LLMQueryGenerator(
        llm=llm_service,
        sql_service=sqlite_service,
    )

    print("=" * 60)
    print("Voice SQL Pipeline Test")
    print("=" * 60)

    while True:
        user_question = input("\nAsk a question (or 'exit'): ").strip()

        if user_question.lower() == "exit":
            break

        if not user_question:
            print("Question cannot be empty.")
            continue

        # Generate SQL
        response = query_generator.generate_query(user_question)

        if response.status == "error":
            print("\n❌ Error")
            print(response.error)
            continue

        print("\nGenerated SQL:")
        print(response.sql)

        # Execute SQL
        try:
            result = sqlite_service.execute(response.sql)

            print("\nResult:")
            print(result)

        except Exception as e:
            print("\nSQLite Execution Error")
            print(e)


if __name__ == "__main__":
    main()