import io
import uuid
from app.services.file_storage import save_file_to_minio

async def process_uploaded_file(file, user, case_id: str = None):
    file_path = await save_file_to_minio(file, str(user.id))
    content = await file.read()
    await file.seek(0)
    try:
        text = content.decode('utf-8', errors='ignore')[:5000]
    except:
        text = ""
    return {
        "id": str(uuid.uuid4()),
        "title": file.filename,
        "file_path": file_path,
        "file_type": file.filename.split('.')[-1].lower() if '.' in file.filename else '',
        "extracted_text": text,
        "case_id": case_id,
        "status": "draft"
    }
