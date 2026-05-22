from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from openai import OpenAI
import os
from app.database import get_db
from app.models.documento_legal import DocumentoLegal
from app.core.embeddings import generar_embedding

router = APIRouter()

SYSTEM_ANALISTA = """Eres INSPOL LEGAL AI, analista jurídico mexicano. Analiza contratos y proporciona:
1. Resumen del documento
2. Riesgos detectados
3. Recomendaciones legales
4. Propuesta de modificación o contrademanda si aplica"""

@router.post("/contrato")
async def analizar_contrato(
    file: UploadFile = File(...),
    tipo_analisis: str = Form("completo"),
    db: AsyncSession = Depends(get_db)
):
    contenido = ""
    try:
        if file.filename.endswith('.pdf'):
            try:
                import PyPDF2, io
                reader = PyPDF2.PdfReader(io.BytesIO(await file.read()))
                contenido = "\n".join([p.extract_text() or "" for p in reader.pages])
            except:
                contenido = (await file.read()).decode('utf-8', errors='ignore')
        else:
            contenido = (await file.read()).decode('utf-8', errors='ignore')
    except Exception as e:
        raise HTTPException(400, f"Error al leer archivo: {str(e)}")
    
    if len(contenido.strip()) < 20:
        raise HTTPException(400, "El documento está vacío o es muy corto")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(500, "OPENAI_API_KEY no configurada")
    
    client = OpenAI(api_key=api_key)
    
    prompt = f"""Analiza este documento legal mexicano:

{contenido[:3000]}

Proporciona un análisis con:
1. RESUMEN
2. RIESGOS
3. RECOMENDACIONES
4. PROPUESTA o CONTRADEMANDA (si aplica)"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_ANALISTA},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=1200
        )
        analisis = response.choices[0].message.content
        
        try:
            emb = generar_embedding(analisis[:500])
            db.add(DocumentoLegal(
                titulo=f"Análisis: {file.filename}",
                contenido=analisis,
                embedding=emb,
                fuente="Análisis IA",
                articulo="Documento analizado"
            ))
            await db.commit()
        except:
            pass
        
        return {
            "nombre_archivo": file.filename,
            "analisis": analisis,
            "aprendizaje": "Análisis guardado en la base de conocimiento"
        }
    except Exception as e:
        raise HTTPException(500, f"Error al analizar: {str(e)}")

@router.post("/expediente/{expediente_id}")
async def analizar_expediente(
    expediente_id: int,
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    from app.models.expediente import Expediente
    exp = await db.get(Expediente, expediente_id)
    if not exp:
        raise HTTPException(404, "Expediente no encontrado")
    
    contenido = ""
    if file:
        try:
            if file.filename.endswith('.pdf'):
                import PyPDF2, io
                reader = PyPDF2.PdfReader(io.BytesIO(await file.read()))
                contenido = "\n".join([p.extract_text() or "" for p in reader.pages])
            else:
                contenido = (await file.read()).decode('utf-8', errors='ignore')
        except:
            raise HTTPException(400, "Error al leer archivo")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(500, "OPENAI_API_KEY no configurada")
    client = OpenAI(api_key=api_key)
    
    prompt = f"""Analiza este expediente legal mexicano:
EXPEDIENTE: {exp.numero_expediente}
CLIENTE: {exp.cliente}
JUZGADO: {exp.juzgado or 'No especificado'}
ESTADO: {exp.estado}
PRIORIDAD: {exp.prioridad}
DESCRIPCIÓN: {exp.descripcion or 'Sin descripción'}
FECHA APERTURA: {exp.fecha_apertura}
DOCUMENTO ADJUNTO: {contenido[:2000] if contenido else 'No se adjuntó documento'}

Proporciona:
1. Análisis del caso
2. Estrategia legal recomendada
3. Próximos pasos procesales
4. Riesgos y oportunidades"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": SYSTEM_ANALISTA}, {"role": "user", "content": prompt}],
        temperature=0.4, max_tokens=1200
    )
    analisis = response.choices[0].message.content
    
    try:
        emb = generar_embedding(analisis[:500])
        db.add(DocumentoLegal(titulo=f"Análisis {exp.numero_expediente}", contenido=analisis, embedding=emb, fuente=f"Expediente {exp.numero_expediente}", articulo="Análisis IA"))
        await db.commit()
    except: pass
    
    return {"expediente": exp.numero_expediente, "analisis": analisis}
