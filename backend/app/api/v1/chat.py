from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from openai import AsyncOpenAI
from app.core.config import settings
from app.services.ai_engine import analyze_contract
from app.services.rag_memory import get_memory
import io

router = APIRouter()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

@router.post("/multimodal")
async def chat_multimodal(
    message: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    context = ""
    file_analysis = None
    memory = await get_memory()

    if file:
        content = await file.read()
        filename = file.filename.lower()

        if filename.endswith(('.pdf', '.docx', '.doc', '.txt', '.png', '.jpg', '.jpeg')):
            if filename.endswith('.pdf'):
                try:
                    from pypdf import PdfReader
                    pdf = PdfReader(io.BytesIO(content))
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                except:
                    text = "No se pudo extraer texto del PDF."
            elif filename.endswith('.docx'):
                try:
                    from docx import Document as DocxDocument
                    doc = DocxDocument(io.BytesIO(content))
                    text = "\n".join([para.text for para in doc.paragraphs])
                except:
                    text = "No se pudo extraer texto del DOCX."
            elif filename.endswith('.txt'):
                text = content.decode('utf-8', errors='ignore')
            else:
                text = "OCR no disponible."

            try:
                file_analysis = await analyze_contract(text)
                context = f"Documento analizado ({filename}):\n{text[:2000]}"
                await memory.store_case_metric({
                    "title": filename,
                    "action": "contrato_revisado",
                    "time_saved": 45,
                    "money_saved": 150,
                    "result": "pendiente"
                })
            except Exception as e:
                file_analysis = {"error": str(e)}
                context = f"Error al analizar: {str(e)}"

        elif filename.endswith(('.mp3', '.wav', '.m4a', '.ogg', '.webm')):
            try:
                transcript = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=(filename, content)
                )
                summary_resp = await client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "Resume esta transcripción jurídica."},
                        {"role": "user", "content": transcript.text}
                    ]
                )
                file_analysis = {
                    "transcription": transcript.text,
                    "summary": summary_resp.choices[0].message.content
                }
                context = f"Audio transcrito ({filename}):\n{transcript.text[:2000]}"
                await memory.store_case_metric({
                    "title": filename,
                    "action": "transcripcion",
                    "time_saved": 30,
                    "money_saved": 80,
                    "result": "pendiente"
                })
            except Exception as e:
                file_analysis = {"error": str(e)}
                context = f"Error al transcribir: {str(e)}"

    similar_memories = await memory.retrieve_similar(message or "", limit=3)
    memory_context = "\n".join([
        f"Pregunta: {m.get('question', '')}\nRespuesta: {m.get('answer', '')}\nCorrección: {m.get('correction', '')}"
        for m in similar_memories
    ])

    system_prompt = (
        "Eres INSPOL, un asistente jurídico virtual impulsado por inteligencia artificial, "
        "creado por el equipo de INSPOL LEGAL AI, una empresa mexicana especializada en tecnología legal. "
        "Tu propósito es ayudar a abogados y despachos a revisar contratos, analizar documentos legales, "
        "transcribir audiencias y brindar información jurídica precisa y actualizada. "
        "Siempre respondes en español, con un tono profesional pero cercano. "
        "NUNCA mencionas a OpenAI ni a ningún otro proveedor de inteligencia artificial. "
        "Si alguien te pregunta quién te creó, respondes que fuiste desarrollado por INSPOL LEGAL AI, "
        "una plataforma mexicana de tecnología para abogados. "
        "No ofreces consejo legal definitivo; siempre recuerdas al usuario que la decisión final es del abogado."
    )

    if memory_context:
        system_prompt += f"\n\nAquí tienes interacciones anteriores similares que puedes usar como referencia:\n{memory_context}"

    messages = [{"role": "system", "content": system_prompt}]
    if context:
        messages.append({"role": "user", "content": f"Contexto del archivo: {context}"})
    if message:
        messages.append({"role": "user", "content": message})
    else:
        messages.append({"role": "user", "content": "Analiza el archivo adjunto y proporciona una valoración jurídica."})

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        temperature=0.5,
        max_tokens=2000
    )

    answer = response.choices[0].message.content

    await memory.store_interaction(
        question=message or "[archivo adjunto]",
        answer=answer,
        metadata={"file_analysis": file_analysis}
    )

    return {
        "response": answer,
        "file_analysis": file_analysis,
        "similar_interactions": len(similar_memories)
    }
