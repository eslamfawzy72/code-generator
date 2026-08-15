from services.speech_service import SpeechService


def main():
    speech_service = SpeechService(
        model_name="Systran/faster-whisper-small",
        device="cpu",
        compute_type="int8",
    )

    print("=" * 60)
    print("Speech Service Test")
    print("=" * 60)

    while True:
        audio_path = input(
            "\nEnter audio file path (or 'exit'): "
        ).strip()

        if audio_path.lower() == "exit":
            break

        if not audio_path:
            print("Audio path cannot be empty.")
            continue

        response = speech_service.transcribe(audio_path)

        if response.status == "error":
            print("\n❌ Error")
            print(response.error)
            continue

        print("\n✅ Transcription Successful")
        print("-" * 60)
        print(f"Detected Language : {response.language}")
        print(f"Transcribed Text  : {response.text}")
        print("-" * 60)


if __name__ == "__main__":
    main()