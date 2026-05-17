from fastapi import APIRouter, Depends
from app.schemas.ai import ContractAnalysisRequest
from app.core.dependencies import get_current_user
from app.services.ai_engine import analyze_contract

router = APIRouter()

@router.post("/analyze-contract")
async def analyze(request: ContractAnalysisRequest, user = Depends(get_current_user)):
    result = await analyze_contract(request.text, request.context)
    return {"status": "ok", "analysis": result}
