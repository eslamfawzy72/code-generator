from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from schemas.orchestrator_request import OrchestratorRequest
from schemas.explain_response import ExplainResponse
from services.orchestrator_service import OrchestratorService 
from schemas.explain_request import ExplainRequest
from schemas.generate_path_response import GenerateResponse
from schemas.learning_required_response import LearningRequiredResponse
from services.learning_service import LearningService, get_learning_service

router = APIRouter()
@router.post(
    "/orchestrator",
    response_model=ExplainResponse | GenerateResponse | LearningRequiredResponse,
)
async def handle_request(
    request: OrchestratorRequest,
    orchestrator: OrchestratorService = Depends(OrchestratorService.get_orchestrator_service),
):
    return orchestrator.handle_request(
        user_prompt=request.user_prompt,
    )


@router.post("/learn")
async def learn_solution(
    problem: str = Form(...),
    file: UploadFile = File(...),
    learning_service: LearningService = Depends(get_learning_service),
):
    solution_bytes = await file.read()
    try:
        solution = solution_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="Uploaded solution must be UTF-8 encoded.",
        ) from exc

    learning_service.learn(
        problem=problem,
        solution=solution,
        language="python",
    )

    return {
        "success": True,
        "message": "Knowledge stored successfully.",
    }