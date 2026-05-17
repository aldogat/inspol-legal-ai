from fastapi import APIRouter, Depends, UploadFile, File
from app.core.dependencies import get_current_user
import openai
from app.core.config import settings

router = APIRouter()

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...), user = Depends(get_current_user)):
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    transcript = client.audio.transcriptions.create(model="whisper-1", file=file.file)
    summary = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role":"system","content":"Resume esta transcripción jurídica."},{"role":"user","content":transcript.text}]
    )
    return {"status":"ok","transcription":{"text":transcript.text,"summary":summary.choices[0].message.content}}
