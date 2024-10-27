from fastapi import APIRouter
from app.api.routers import (
    health_check,
    transcribe
)

router = APIRouter()

# Health Check routers
router.include_router(health_check.router, prefix="/health", tags=["Health-Check"])

# Transcribe routers
router.include_router(transcribe.router, prefix="/transcribe", tags=["Whisper-Transcribe"])
