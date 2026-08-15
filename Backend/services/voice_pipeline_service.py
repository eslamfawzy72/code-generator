from functools import lru_cache
from fastapi import UploadFile

from services.speech_service import SpeechService
from services.llm_query_generator import LLMQueryGenerator
from services.sql_service import SQLiteService
from services.text_normalizer_service import TextNormalizer
from services.llm_service import LLMService

from schemas.voice_pipeline_response import VoicePipelineResponse


class VoicePipelineService:
    def __init__(
        self,
        speech_service: SpeechService,
        query_generator: LLMQueryGenerator,
        sqlite_service: SQLiteService,
        text_normalizer: TextNormalizer,
    ):
        self.speech_service = speech_service
        self.query_generator = query_generator
        self.sqlite_service = sqlite_service
        self.text_normalizer = text_normalizer

    async def process(self, audio: UploadFile) -> VoicePipelineResponse:
        # -------------------------------
        # Step 1: Speech → Text
        # -------------------------------
        speech_response = await self.speech_service.transcribe(audio)

        if speech_response.status == "error":
            return VoicePipelineResponse(
                status="error",
                error=speech_response.error,
            )

        # -------------------------------
        # Step 2: Text → normalized text
        # -------------------------------
        normalization_response = await self.text_normalizer.normalize(
            speech_response.text
        )
        print(f"Normalization Response: {normalization_response.text}")
        if normalization_response.status == "error":
            return VoicePipelineResponse(
                status="error",
                transcription=speech_response.text,
                detected_language=speech_response.language,
                error=normalization_response.error,
            )
        # -------------------------------
        # Step 3:   normalized text → SQL query
        # -------------------------------
        
        sql_response = self.query_generator.generate_query(
            normalization_response.text
        )

        if sql_response.status == "error":
            return VoicePipelineResponse(
                status="error",
                transcription=speech_response.text,
                detected_language=speech_response.language,
                error=sql_response.error,
            )

        # -------------------------------
        # Step 4: Execute SQL
        # -------------------------------
        try:
            result = self.sqlite_service.execute(sql_response.sql)

            return VoicePipelineResponse(
                status="success",
                transcription=speech_response.text,
                detected_language=speech_response.language,
                sql_query=sql_response.sql,
                result=result,
            )

        except Exception as e:
            return VoicePipelineResponse(
                status="error",
                transcription=speech_response.text,
                detected_language=speech_response.language,
                sql_query=sql_response.sql,
                error=str(e),
            )
            
    @lru_cache()
    def get_voice_pipeline_service():
        return VoicePipelineService(
            speech_service=SpeechService(),
            query_generator=LLMQueryGenerator(
                llm=LLMService(model_name="qwen2.5:3b"),
                sql_service=SQLiteService(db_path="database/data.db"),
            ),
        sqlite_service=SQLiteService(db_path="database/data.db"),
        text_normalizer=TextNormalizer(
            llm=LLMService(model_name="qwen2.5:3b"),
            sql_service=SQLiteService(db_path="database/data.db"),
        ),
    )