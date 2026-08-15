from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from services.voice_pipeline_service import VoicePipelineService
from schemas.voice_pipeline_response import VoicePipelineResponse


router = APIRouter()


@router.post(
    "/voice_pipeline",
    response_model=VoicePipelineResponse,
)
async def voice_pipeline(
    audio: UploadFile = File(...),
    voice_pipeline_service: VoicePipelineService = Depends(
        VoicePipelineService.get_voice_pipeline_service
    ),
):
    response = await voice_pipeline_service.process(audio)

    if response.status == "error":
        raise HTTPException(
            status_code=400,
            detail=response.error,
        )

    return response