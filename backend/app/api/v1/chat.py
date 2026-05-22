from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from openai import OpenAI
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.core.embeddings import generar_embedding

router = APIRouter()

SYSTEM_PROMPT = "Eres INSPOL LEGAL AI, un asistente jurídico mexicano. Responde con precisión citando leyes mexicanas cuando sea posible."

class Consulta(BaseModel):
    consulta: str

@router.post("/multimodal")
async def multimodal_chat(consulta: Consulta, db: AsyncSession = Depends(get_db)):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(500, "OPENAI_API_KEY no configurada")
    
    client = OpenAI(api_key=api_key)
    
    try:
        contexto = ""
        try:
            embedding = generar_embedding(consulta.consulta)
            docs_query = text("SELECT titulo, contenido FROM documentos_legales ORDER BY embedding <=> CAST(:emb AS vector) LIMIT 3")
            docs_result = await db.execute(docs_query, {"emb": str(embedding)})
            docs = docs_result.fetchall()
            if docs:
                contexto = "**Documentos relevantes:**\n"
                for d in docs:
                    contexto += f"- {d.titulo}: {d.contenido[:200]}\n"
        except:
            pass
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if contexto:
            messages.append({"role": "system", "content": contexto})
        messages.append({"role": "user", "content": consulta.consulta})
        
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.4,
            max_tokens=800
        ).choices[0].message.content
        
        return {"respuesta": resp}
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")
