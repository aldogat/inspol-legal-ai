from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.contrato import Contrato
from app.models.cliente import Cliente

router = APIRouter()

class ContratoCreate(BaseModel):
    numero_contrato: str
    cliente_id: int
    fecha_inicio: date
    fecha_vencimiento: date
    estado: Optional[str] = "Activo"
    descripcion: Optional[str] = None

class ContratoUpdate(BaseModel):
    numero_contrato: Optional[str] = None
    cliente_id: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    estado: Optional[str] = None
    descripcion: Optional[str] = None

class ContratoOut(BaseModel):
    id: int
    numero_contrato: str
    cliente_id: int
    fecha_inicio: date
    fecha_vencimiento: date
    estado: str
    descripcion: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    class Config:
        from_attributes = True

@router.post("/", response_model=ContratoOut, status_code=201)
async def crear(con: ContratoCreate, db: AsyncSession = Depends(get_db)):
    if not await db.get(Cliente, con.cliente_id):
        raise HTTPException(404, "Cliente no encontrado")
    if (await db.execute(select(Contrato).where(Contrato.numero_contrato == con.numero_contrato))).scalar_one_or_none():
        raise HTTPException(400, "Número de contrato ya existe")
    nuevo = Contrato(**con.dict())
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=List[ContratoOut])
async def listar(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Contrato).order_by(Contrato.fecha_vencimiento.asc()).offset(skip).limit(limit))
    return r.scalars().all()

@router.get("/{contrato_id}", response_model=ContratoOut)
async def obtener(contrato_id: int, db: AsyncSession = Depends(get_db)):
    c = await db.get(Contrato, contrato_id)
    if not c: raise HTTPException(404)
    return c

@router.put("/{contrato_id}", response_model=ContratoOut)
async def actualizar(contrato_id: int, con_data: ContratoUpdate, db: AsyncSession = Depends(get_db)):
    c = await db.get(Contrato, contrato_id)
    if not c: raise HTTPException(404)
    for k, v in con_data.dict(exclude_unset=True).items():
        setattr(c, k, v)
    await db.commit()
    await db.refresh(c)
    return c

@router.delete("/{contrato_id}", status_code=204)
async def eliminar(contrato_id: int, db: AsyncSession = Depends(get_db)):
    c = await db.get(Contrato, contrato_id)
    if not c: raise HTTPException(404)
    await db.delete(c)
    await db.commit()
