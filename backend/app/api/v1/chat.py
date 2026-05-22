from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from openai import OpenAI
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.conversacion import Conversacion
from app.models.documento_legal import DocumentoLegal
from app.core.embeddings import generar_embedding

router = APIRouter()

SYSTEM_PROMPT = """Eres INSPOL LEGAL AI PRO MX, un copiloto jurídico de alto nivel para abogados mexicanos.  
Actúas como un abogado sénior especializado en derecho mexicano. Tu función es **siempre** ayudar a redactar, analizar y proponer, nunca decir "no puedo".  

## ÁMBITO LEGAL
Dominas toda la legislación federal (Constitución, Códigos Civil, Penal, de Comercio, Nacional de Procedimientos Civiles y Familiares, Ley de Amparo, LFT, LGSM, etc.) y la estatal que indique el usuario.  

## CAPACIDADES
- Redactar demandas, contestaciones, reconvenciones, contrademandas y todo tipo de escritos judiciales.  
- Analizar contratos: extraer obligaciones, detectar riesgos, cláusulas abusivas, ambigüedades y proponer mejoras.  
- Hacer investigación jurídica: normas aplicables, conceptos, riesgos, preguntas abiertas.  
- Resumir documentos, generar cronologías, preparar preguntas para audiencias.  
- Siempre que exista base legal, redactar borradores completos, citando artículos cuando sea posible.  

## REGLAS OBLIGATORIAS
1. **Nunca inventes** artículos, jurisprudencia, hechos o fechas. Si no tienes certeza, indica "PENDIENTE DE CONFIRMAR".  
2. **Siempre distingue** entre hechos confirmados, suposiciones, riesgos e información faltante.  
3. **Cuando exista incertidumbre** agrega "Requiere validación jurídica".  
4. **Al redactar escritos** solicita primero los datos esenciales (actor, demandado, juzgado, hechos, pruebas, pretensiones) y luego genera el documento completo con encabezado, competencia, partes, hechos, fundamentos, pruebas, peticiones y firma.  
5. **Eres un asistente de IA, no un abogado certificado**, pero eso no te impide redactar borradores profesionales. Siempre recuerda que el documento final debe ser revisado por un abogado.  

## FORMATO DE RESPUESTA
- Lenguaje jurídico profesional, claro y ordenado.  
- Usa viñetas, negritas y secciones para facilitar la lectura.  
- Cuando uses la base de conocimiento (RAG), cita la fuente (Código, artículo).  

## USO DE LA BASE DE CONOCIMIENTO
Si encuentras documentos relevantes en el contexto proporcionado, utilízalos para fundamentar tu respuesta e indícalo con "📚 Basado en documentos de la base de conocimiento"."""

class Consulta(BaseModel):
    consulta: str

class MensajeOut(BaseModel):
    id: int
    rol: str
    contenido: str
    created_at: datetime
    class Config:
        from_attributes = True

@router.post("/multimodal")
async def multimodal_chat(consulta: Consulta, db: AsyncSession = Depends(get_db)):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(500, "OPENAI_API_KEY no configurada")
    
    client = OpenAI(api_key=api_key)
    
    try:
        # Guardar mensaje del usuario
        user_msg = Conversacion(user_id=1, rol="user", contenido=consulta.consulta)
        db.add(user_msg)
        await db.commit()
        
        # Buscar contexto RAG
        contexto = ""
        try:
            embedding = generar_embedding(consulta.consulta)
            docs_query = text("SELECT titulo, contenido, fuente, articulo FROM documentos_legales ORDER BY embedding <=> CAST(:emb AS vector) LIMIT 3")
            docs_result = await db.execute(docs_query, {"emb": str(embedding)})
            docs = docs_result.fetchall()
            if docs:
                contexto = "**Documentos legales encontrados en la base de conocimiento:**\n"
                for d in docs:
                    contexto += f"📄 {d.titulo}\n   Fuente: {d.fuente or 'N/A'}"
                    if d.articulo:
                        contexto += f", {d.articulo}"
                    contexto += f"\n   Contenido: {d.contenido[:500]}\n\n"
                contexto += "Usa esta información para fundamentar tu respuesta.\n\n"
        except:
            pass
        
        # Obtener historial para contexto
        historial = await db.execute(
            select(Conversacion)
            .where(Conversacion.user_id == 1)
            .order_by(Conversacion.created_at.desc())
            .limit(10)
        )
        mensajes_previos = historial.scalars().all()
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if contexto:
            messages.append({"role": "system", "content": contexto})
        for msg in reversed(mensajes_previos):
            messages.append({"role": msg.rol, "content": msg.contenido})
        messages.append({"role": "user", "content": consulta.consulta})
        
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.3,
            max_tokens=2000
        ).choices[0].message.content
        
        # Guardar respuesta
        assistant_msg = Conversacion(user_id=1, rol="assistant", contenido=resp)
        db.add(assistant_msg)
        await db.commit()
        
        return {"respuesta": resp}
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")

@router.get("/historial", response_model=List[MensajeOut])
async def obtener_historial(skip: int=0, limit: int=50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Conversacion)
        .where(Conversacion.user_id == 1)
        .order_by(Conversacion.created_at.asc())
        .offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.delete("/historial", status_code=204)
async def borrar_historial(db: AsyncSession = Depends(get_db)):
    await db.execute(Conversacion.__table__.delete().where(Conversacion.user_id == 1))
    await db.commit()
    return None
