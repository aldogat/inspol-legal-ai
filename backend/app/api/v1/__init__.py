from fastapi import APIRouter

from .auth import router as auth_router
from .ai import router as ai_router
from .chat import router as chat_router
from .documents import router as documents_router
from .approvals import router as approvals_router
from .transcription import router as transcription_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_v1_router.include_router(ai_router, prefix="/ai", tags=["ai"])
api_v1_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_v1_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_v1_router.include_router(approvals_router, prefix="/approvals", tags=["approvals"])
api_v1_router.include_router(transcription_router, prefix="/transcription", tags=["transcription"])
