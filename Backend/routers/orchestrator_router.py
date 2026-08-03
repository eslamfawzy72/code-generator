from fastapi import APIRouter, Depends

from schemas.explain_response import ExplainResponse
from services.orchestrator_service import OrchestratorService 
from schemas.explain_request import ExplainRequest

router = APIRouter()

@router.post("/explain",response_model=ExplainResponse)
async def explain_code( request: ExplainRequest, 
                       orchestrator: OrchestratorService = 
                       Depends(OrchestratorService.get_orchestrator_service)):
    """
    Endpoint to handle code explanation requests.

    Args:
        request (ExplainRequest): The request containing the user prompt and source code.
        orchestrator (OrchestratorService): The orchestrator service dependency.

    Returns:
        ExplainResponse: The response containing the explanation.
    """
    return orchestrator.handle_request(user_prompt=request.user_prompt, source_code=request.source_code)