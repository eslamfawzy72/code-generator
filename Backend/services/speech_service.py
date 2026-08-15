import os
from pathlib import Path
import tempfile
import time
from fastapi import UploadFile
from faster_whisper import WhisperModel

from schemas.speech_response import SpeechResponse


class SpeechService:
    def __init__(
        self,
        model_name: str = "Systran/faster-whisper-small",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        print("=" * 60)
        print("Initializing Whisper Model...")
        print(f"Model        : {model_name}")
        print(f"Device       : {device}")
        print(f"Compute Type : {compute_type}")

        start = time.time()

        self.model = WhisperModel(
            model_name,
            device=device,
            compute_type=compute_type,
            download_root="D:/huggingface_models",
        )

        print(f"Model loaded in {time.time() - start:.2f} seconds")
        print("=" * 60)

    async def transcribe(self, audio: UploadFile) -> SpeechResponse:
        try:
            print("\nStarting transcription...")
            print(f"Audio file: {audio.filename}")

            suffix = os.path.splitext(audio.filename)[1]

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
            ) as temp_file:

                content = await audio.read()
                temp_file.write(content)

                temp_path = temp_file.name

            print(f"Temporary audio file: {temp_path}")
            print(f"File size: {len(content) / 1024:.2f} KB")

            segments, info = self.model.transcribe(
                temp_path,
                beam_size=5,
                vad_filter=True,
            )

            print(f"Language detected: {info.language}")
            print(
                f"Language probability: "
                f"{info.language_probability:.3f}"
            )

            text_parts = []

            print("\nSegments:")
            print("-" * 60)

            for segment in segments:
                print(
                    f"[{segment.start:.2f}s -> "
                    f"{segment.end:.2f}s] "
                    f"{segment.text}"
                )

                text_parts.append(
                    segment.text.strip()
                )

            text = " ".join(text_parts).strip()

            print("-" * 60)
            print(f"Final text: {text}")

            return SpeechResponse(
                status="success",
                text=text,
            )

        except Exception as e:
            print("\nException occurred!")
            print(type(e).__name__)
            print(e)

            return SpeechResponse(
                status="error",
                error=str(e),
            )

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"Temporary file removed: {temp_path}")