from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.transaccion import Transaccion

router = APIRouter()

class TransaccionCreate(BaseModel):
    tipo: str
    categoria: str
    monto: float
    fecha: datetime
    descripcion: Optional[str] = None

class TransaccionUpdate(BaseModel):
    tipo: Optional[str] = None
    categoria: Optional[str] = None
    monto: Optional[float] = None
    fecha: Optional[datetime] = None
    descripcion: Optional[str] = None

class TransaccionOut(BaseModel):
    id: int
    tipo: str
    categoria: str
    monto: float
    fecha: datetime
    descripcion: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    class Config:
        from_attributes = True

class ResumenOut(BaseModel):
    total_ingresos: float
    total_gastos: float
    balance: float
    total_transacciones: int

@router.post("/", response_model=TransaccionOut, status_code=201)
async def crear(trans: TransaccionCreate, db: AsyncSession = Depends(get_db)):
    if trans.tipo not in ("Ingreso", "Gasto"):
        raise HTTPException(400, "Tipo inválido")
    nuevo = Transaccion(**trans.dict())
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=List[TransaccionOut])
async def listar(skip: int = 0, limit: int = 100, tipo: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(Transaccion)
    if tipo: query = query.where(Transaccion.tipo == tipo)
    r = await db.execute(query.order_by(Transaccion.fecha.desc()).offset(skip).limit(limit))
    return r.scalars().all()

@router.get("/resumen", response_model=ResumenOut)
async def resumen(db: AsyncSession = Depends(get_db)):
    ingresos = (await db.execute(select(func.coalesce(func.sum(Transaccion.monto), 0)).where(Transaccion.tipo == "Ingreso"))).scalar() or 0
    gastos = (await db.execute(select(func.coalesce(func.sum(Transaccion.monto), 0)).where(Transaccion.tipo == "Gasto"))).scalar() or 0
    total = (await db.execute(select(func.count(Transaccion.id)))).scalar() or 0
    return {"total_ingresos": ingresos, "total_gastos": gastos, "balance": ingresos - gastos, "total_transacciones": total}

@router.get("/{transaccion_id}", response_model=TransaccionOut)
async def obtener(transaccion_id: int, db: AsyncSession = Depends(get_db)):
    t = await db.get(Transaccion, transaccion_id)
    if not t: raise HTTPException(404)
    return t

@router.put("/{transaccion_id}", response_model=TransaccionOut)
async def actualizar(transaccion_id: int, trans_data: TransaccionUpdate, db: AsyncSession = Depends(get_db)):
    t = await db.get(Transaccion, transaccion_id)
    if not t: raise HTTPException(404)
    for k, v in trans_data.dict(exclude_unset=True).items():
        setattr(t, k, v)
    await db.commit()
    await db.refresh(t)
    return t

@router.delete("/{transaccion_id}", status_code=204)
async def eliminar(transaccion_id: int, db: AsyncSession = Depends(get_db)):
    t = await db.get(Transaccion, transaccion_id)
    if not t: raise HTTPException(404)
    await db.delete(t)
    await db.commit()
