from fastapi import APIRouter, Depends

from schemas.orchestrator_request import OrchestratorRequest
from schemas.explain_response import ExplainResponse
from services.orchestrator_service import OrchestratorService 
from schemas.explain_request import ExplainRequest
from schemas.generate_path_response import GenerateResponse

router = APIRouter()
@router.post(
    "/orchestrator",
    response_model=ExplainResponse | GenerateResponse,
)
async def handle_request(
    request: OrchestratorRequest,
    orchestrator: OrchestratorService = Depends(OrchestratorService.get_orchestrator_service),
):
    return orchestrator.handle_request(
        user_prompt=request.user_prompt,
    )