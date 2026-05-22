from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.historial import HistorialExpediente, HistorialContrato

router = APIRouter()

class HistorialOut(BaseModel):
    id: int
    accion: str
    descripcion: str | None
    usuario_id: int | None
    created_at: datetime
    class Config: from_attributes = True

@router.get("/expedientes/{numero_expediente}", response_model=List[HistorialOut])
async def historial_expediente(numero_expediente: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(
        select(HistorialExpediente)
        .where(HistorialExpediente.numero_expediente == numero_expediente)
        .order_by(HistorialExpediente.created_at.desc())
        .limit(50)
    )
    return r.scalars().all()

@router.get("/contratos/{numero_contrato}", response_model=List[HistorialOut])
async def historial_contrato(numero_contrato: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(
        select(HistorialContrato)
        .where(HistorialContrato.numero_contrato == numero_contrato)
        .order_by(HistorialContrato.created_at.desc())
        .limit(50)
    )
    return r.scalars().all()
