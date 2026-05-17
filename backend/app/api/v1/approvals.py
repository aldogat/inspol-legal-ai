from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.dependencies import get_current_user

router = APIRouter()

class ApprovalRequest(BaseModel):
    document_id: str
    action: str
    comments: str = ""

@router.post("/submit")
async def submit_approval(request: ApprovalRequest, user = Depends(get_current_user)):
    new_status = "approved" if request.action == "approve" else "draft"
    return {"status": "ok", "document_id": request.document_id, "new_status": new_status}
