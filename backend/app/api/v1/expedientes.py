from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.expediente import Expediente

router = APIRouter()

class ExpedienteCreate(BaseModel):
    numero_expediente: str
    cliente: str
    juzgado: Optional[str] = None
    estado: Optional[str] = "Activo"
    prioridad: Optional[str] = "Media"
    descripcion: Optional[str] = None
    fecha_apertura: date

class ExpedienteUpdate(BaseModel):
    numero_expediente: Optional[str] = None
    cliente: Optional[str] = None
    juzgado: Optional[str] = None
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_apertura: Optional[date] = None

class ExpedienteOut(BaseModel):
    id: int
    numero_expediente: str
    cliente: str
    juzgado: Optional[str]
    estado: str
    prioridad: str
    descripcion: Optional[str]
    fecha_apertura: date
    created_at: datetime
    updated_at: Optional[datetime]
    class Config:
        from_attributes = True

@router.post("/", response_model=ExpedienteOut, status_code=201)
async def crear(exp: ExpedienteCreate, db: AsyncSession = Depends(get_db)):
    if (await db.execute(select(Expediente).where(Expediente.numero_expediente == exp.numero_expediente))).scalar_one_or_none():
        raise HTTPException(400, "Número de expediente ya existe")
    nuevo = Expediente(**exp.dict())
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=List[ExpedienteOut])
async def listar(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Expediente).order_by(Expediente.fecha_apertura.desc()).offset(skip).limit(limit))
    return r.scalars().all()

@router.get("/{expediente_id}", response_model=ExpedienteOut)
async def obtener(expediente_id: int, db: AsyncSession = Depends(get_db)):
    e = await db.get(Expediente, expediente_id)
    if not e: raise HTTPException(404)
    return e

@router.put("/{expediente_id}", response_model=ExpedienteOut)
async def actualizar(expediente_id: int, exp_data: ExpedienteUpdate, db: AsyncSession = Depends(get_db)):
    e = await db.get(Expediente, expediente_id)
    if not e: raise HTTPException(404)
    for k, v in exp_data.dict(exclude_unset=True).items():
        setattr(e, k, v)
    await db.commit()
    await db.refresh(e)
    return e

@router.delete("/{expediente_id}", status_code=204)
async def eliminar(expediente_id: int, db: AsyncSession = Depends(get_db)):
    e = await db.get(Expediente, expediente_id)
    if not e: raise HTTPException(404)
    await db.delete(e)
    await db.commit()
