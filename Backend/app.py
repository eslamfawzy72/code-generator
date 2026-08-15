from fastapi import FastAPI

from routers.orchestrator_router import router as orchestrator_router
from routers.voice_analysis_router import router as voice_analysis_router

app = FastAPI(
    title="Code Generation & Explanation API",
    version="1.0.0",
)

app.include_router(orchestrator_router, prefix="/api/v1")
app.include_router(voice_analysis_router, prefix="/api/v1")
