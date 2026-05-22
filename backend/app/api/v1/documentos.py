from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import PyPDF2
import io

from app.database import get_db
from app.models.documento_legal import DocumentoLegal
from app.core.embeddings import generar_embedding

router = APIRouter()

class DocumentoCreate(BaseModel):
    titulo: str
    contenido: str
    fuente: Optional[str] = None
    articulo: Optional[str] = None

class DocumentoOut(BaseModel):
    id: int
    titulo: str
    contenido: str
    fuente: Optional[str] = None
    articulo: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

@router.post("/", response_model=DocumentoOut, status_code=201)
async def crear_documento(doc: DocumentoCreate, db: AsyncSession = Depends(get_db)):
    embedding = generar_embedding(doc.contenido)
    nuevo_doc = DocumentoLegal(
        titulo=doc.titulo,
        contenido=doc.contenido,
        embedding=embedding,
        fuente=doc.fuente,
        articulo=doc.articulo
    )
    db.add(nuevo_doc)
    await db.commit()
    await db.refresh(nuevo_doc)
    return nuevo_doc

@router.post("/cargar-pdf")
async def cargar_pdf(
    file: UploadFile = File(...),
    fuente: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Solo se aceptan archivos PDF")
    
    contenido = ""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(await file.read()))
        for pagina in pdf_reader.pages:
            texto = pagina.extract_text()
            if texto:
                contenido += texto + "\n"
    except Exception as e:
        raise HTTPException(500, f"Error al leer PDF: {str(e)}")
    
    if not contenido.strip():
        raise HTTPException(400, "No se pudo extraer texto del PDF")
    
    fragmentos = []
    palabras = contenido.split()
    fragmento_actual = ""
    for palabra in palabras:
        if len(fragmento_actual) + len(palabra) < 500:
            fragmento_actual += palabra + " "
        else:
            fragmentos.append(fragmento_actual.strip())
            fragmento_actual = palabra + " "
    if fragmento_actual:
        fragmentos.append(fragmento_actual.strip())
    
    docs_creados = 0
    for i, fragmento in enumerate(fragmentos):
        embedding = generar_embedding(fragmento)
        doc = DocumentoLegal(
            titulo=f"{file.filename} - Fragmento {i+1}",
            contenido=fragmento,
            embedding=embedding,
            fuente=fuente or file.filename
        )
        db.add(doc)
        docs_creados += 1
    
    await db.commit()
    return {"mensaje": f"Documento cargado exitosamente", "fragmentos": docs_creados}

@router.get("/", response_model=List[DocumentoOut])
async def listar_documentos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DocumentoLegal).offset(skip).limit(limit).order_by(DocumentoLegal.created_at.desc())
    )
    return result.scalars().all()

@router.delete("/{doc_id}", status_code=204)
async def eliminar_documento(doc_id: int, db: AsyncSession = Depends(get_db)):
    doc = await db.get(DocumentoLegal, doc_id)
    if not doc:
        raise HTTPException(404, "Documento no encontrado")
    await db.delete(doc)
    await db.commit()
    return None
