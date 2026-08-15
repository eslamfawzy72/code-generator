from services.speech_service import SpeechService
from services.llm_service import LLMService
from services.text_normalizer_service import TextNormalizer
from services.llm_query_generator import LLMQueryGenerator
from services.sql_service import SQLiteService


def main():
    print("=" * 60)
    print("FULL VOICE SQL PIPELINE TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # Initialize services
    # ---------------------------------------------------------

    print("\nInitializing services...")

    speech_service = SpeechService(
        model_name="Systran/faster-whisper-small",
        device="cpu",
        compute_type="int8",
    )

    llm_service = LLMService()

    sqlite_service = SQLiteService(
        db_path="database/data.db"
    )

    text_normalizer = TextNormalizer(
        llm=llm_service,
        sql_service=sqlite_service,
    )

    query_generator = LLMQueryGenerator(
        llm=llm_service,
        sql_service=sqlite_service,
    )

    print("Services initialized successfully.")

    # ---------------------------------------------------------
    # Pipeline
    # ---------------------------------------------------------

    while True:
        print("\n" + "=" * 60)

        audio_path = input(
            "Enter audio file path (or 'exit'): "
        ).strip()

        if audio_path.lower() == "exit":
            break

        if not audio_path:
            print("Audio path cannot be empty.")
            continue

        # =====================================================
        # STEP 1: Speech -> Text
        # =====================================================

        print("\n" + "-" * 60)
        print("STEP 1: Speech -> Text")
        print("-" * 60)

        speech_response = speech_service.transcribe(
            audio_path
        )

        if speech_response.status == "error":
            print("❌ Speech transcription failed")
            print(f"Error: {speech_response.error}")
            continue

        print("✅ Speech transcription successful")
        print(f"Raw transcription: {speech_response.text}")

        # =====================================================
        # STEP 2: Text Normalization
        # =====================================================

        print("\n" + "-" * 60)
        print("STEP 2: Text Normalization")
        print("-" * 60)

        normalization_response = text_normalizer.normalize(
            speech_response.text
        )

        if normalization_response.status == "error":
            print("❌ Text normalization failed")
            print(f"Error: {normalization_response.error}")
            continue

        print("✅ Text normalization successful")
        print(f"Raw text       : {speech_response.text}")
        print(
            f"Normalized text: {normalization_response.text}"
        )

        # =====================================================
        # STEP 3: Text -> SQL
        # =====================================================

        print("\n" + "-" * 60)
        print("STEP 3: Text -> SQL")
        print("-" * 60)

        query_response = query_generator.generate_query(
            normalization_response.text
        )

        if query_response.status == "error":
            print("❌ SQL generation failed")
            print(f"Error: {query_response.error}")
            continue

        print("✅ SQL generation successful")
        print(f"Generated SQL:\n{query_response.sql}")

        # =====================================================
        # STEP 4: SQL -> SQLite
        # =====================================================

        print("\n" + "-" * 60)
        print("STEP 4: SQL -> SQLite")
        print("-" * 60)

        try:
            result = sqlite_service.execute(
                query_response.sql
            )

            print("✅ SQL execution successful")
            print("\nResult:")
            print(result)

        except Exception as e:
            print("❌ SQL execution failed")
            print(f"Error: {e}")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    main()