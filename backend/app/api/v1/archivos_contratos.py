from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
from pydantic import BaseModel
import os, shutil, PyPDF2

from app.database import get_db
from app.models.archivo_contrato import ArchivoContrato
from app.models.contrato import Contrato
from app.models.documento_legal import DocumentoLegal
from app.core.embeddings import generar_embedding

router = APIRouter()
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads", "contratos")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ArchivoOut(BaseModel):
    id: int; contrato_id: int; nombre_original: str; tipo: str | None; tamanio: int | None; created_at: datetime
    class Config: from_attributes = True

def extraer_texto_pdf(ruta: str) -> str:
    try:
        with open(ruta, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join([p.extract_text() or "" for p in reader.pages])
    except: return ""

@router.post("/contratos/{contrato_id}/archivos", response_model=ArchivoOut, status_code=201)
async def subir_archivo(contrato_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    con = await db.get(Contrato, contrato_id)
    if not con: raise HTTPException(404, "Contrato no encontrado")
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    nombre = f"{contrato_id}_{ts}_{file.filename}"
    ruta = os.path.join(UPLOAD_DIR, nombre)
    with open(ruta, "wb") as b: shutil.copyfileobj(file.file, b)
    file.file.close()
    arch = ArchivoContrato(contrato_id=contrato_id, nombre_original=file.filename, nombre_guardado=nombre, ruta=ruta, tipo=file.content_type or "application/octet-stream", tamanio=os.path.getsize(ruta))
    db.add(arch)
    
    texto = ""
    if file.content_type == "application/pdf": texto = extraer_texto_pdf(ruta)
    if texto.strip():
        embedding = generar_embedding(texto[:1000])
        doc = DocumentoLegal(titulo=f"Contrato {con.numero_contrato} - {file.filename}", contenido=texto[:2000], embedding=embedding, fuente=f"Contrato {con.numero_contrato}", articulo=None)
        db.add(doc)
    
    await db.commit(); await db.refresh(arch); return arch

@router.get("/contratos/{contrato_id}/archivos", response_model=List[ArchivoOut])
async def listar(contrato_id: int, db: AsyncSession = Depends(get_db)):
    if not await db.get(Contrato, contrato_id): raise HTTPException(404)
    r = await db.execute(select(ArchivoContrato).where(ArchivoContrato.contrato_id == contrato_id).order_by(ArchivoContrato.created_at.desc()))
    return r.scalars().all()

@router.get("/archivos-contratos/{archivo_id}/descargar")
async def descargar(archivo_id: int, db: AsyncSession = Depends(get_db)):
    a = await db.get(ArchivoContrato, archivo_id)
    if not a or not os.path.exists(a.ruta): raise HTTPException(404)
    return FileResponse(a.ruta, filename=a.nombre_original, media_type=a.tipo or "application/octet-stream")

@router.delete("/archivos-contratos/{archivo_id}", status_code=204)
async def eliminar(archivo_id: int, db: AsyncSession = Depends(get_db)):
    a = await db.get(ArchivoContrato, archivo_id)
    if not a: raise HTTPException(404)
    if os.path.exists(a.ruta): os.remove(a.ruta)
    await db.delete(a); await db.commit()
