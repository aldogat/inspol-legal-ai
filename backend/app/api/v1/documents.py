from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.core.dependencies import get_current_user
from app.services.document_processor import process_uploaded_file

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    case_id: str = Form(None),
    user = Depends(get_current_user)
):
    document = await process_uploaded_file(file, user, case_id)
    return {"status": "ok", "document": document}
