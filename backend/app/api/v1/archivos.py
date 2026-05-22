from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
from pydantic import BaseModel
import os, shutil, PyPDF2, io

from app.database import get_db
from app.models.archivo import ArchivoAdjunto
from app.models.expediente import Expediente
from app.models.documento_legal import DocumentoLegal
from app.core.embeddings import generar_embedding

router = APIRouter()
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ArchivoOut(BaseModel):
    id: int; expediente_id: int; nombre_original: str; tipo: str | None; tamanio: int | None; created_at: datetime
    class Config: from_attributes = True

def extraer_texto_pdf(ruta: str) -> str:
    try:
        with open(ruta, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join([p.extract_text() or "" for p in reader.pages])
    except: return ""

@router.post("/expedientes/{expediente_id}/archivos", response_model=ArchivoOut, status_code=201)
async def subir_archivo(expediente_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    exp = await db.get(Expediente, expediente_id)
    if not exp: raise HTTPException(404, "Expediente no encontrado")
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    nombre = f"{expediente_id}_{ts}_{file.filename}"
    ruta = os.path.join(UPLOAD_DIR, nombre)
    with open(ruta, "wb") as b: shutil.copyfileobj(file.file, b)
    file.file.close()
    arch = ArchivoAdjunto(expediente_id=expediente_id, nombre_original=file.filename, nombre_guardado=nombre, ruta=ruta, tipo=file.content_type or "application/octet-stream", tamanio=os.path.getsize(ruta))
    db.add(arch)
    
    # Extraer texto e indexar para RAG
    texto = ""
    if file.content_type == "application/pdf": texto = extraer_texto_pdf(ruta)
    if texto.strip():
        embedding = generar_embedding(texto[:1000])
        doc = DocumentoLegal(titulo=f"Exp.{exp.numero_expediente} - {file.filename}", contenido=texto[:2000], embedding=embedding, fuente=f"Expediente {exp.numero_expediente}", articulo=None)
        db.add(doc)
    
    await db.commit(); await db.refresh(arch); return arch

@router.get("/expedientes/{expediente_id}/archivos", response_model=List[ArchivoOut])
async def listar(expediente_id: int, db: AsyncSession = Depends(get_db)):
    if not await db.get(Expediente, expediente_id): raise HTTPException(404)
    r = await db.execute(select(ArchivoAdjunto).where(ArchivoAdjunto.expediente_id == expediente_id).order_by(ArchivoAdjunto.created_at.desc()))
    return r.scalars().all()

@router.get("/archivos/{archivo_id}/descargar")
async def descargar(archivo_id: int, db: AsyncSession = Depends(get_db)):
    a = await db.get(ArchivoAdjunto, archivo_id)
    if not a or not os.path.exists(a.ruta): raise HTTPException(404)
    return FileResponse(a.ruta, filename=a.nombre_original, media_type=a.tipo or "application/octet-stream")

@router.delete("/archivos/{archivo_id}", status_code=204)
async def eliminar(archivo_id: int, db: AsyncSession = Depends(get_db)):
    a = await db.get(ArchivoAdjunto, archivo_id)
    if not a: raise HTTPException(404)
    if os.path.exists(a.ruta): os.remove(a.ruta)
    await db.delete(a); await db.commit()
