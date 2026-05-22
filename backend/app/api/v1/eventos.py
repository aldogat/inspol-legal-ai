from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.evento import Evento

router = APIRouter()

# ---------- Esquemas ----------
class EventoCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha_inicio: datetime
    fecha_fin: datetime
    tipo: Optional[str] = "Reunión"
    ubicacion: Optional[str] = None
    color: Optional[str] = "#3b82f6"

class EventoUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    tipo: Optional[str] = None
    ubicacion: Optional[str] = None
    color: Optional[str] = None

class EventoOut(BaseModel):
    id: int
    titulo: str
    descripcion: Optional[str] = None
    fecha_inicio: datetime
    fecha_fin: datetime
    tipo: str
    ubicacion: Optional[str] = None
    color: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

# ---------- Endpoints ----------
@router.post("/", response_model=EventoOut, status_code=status.HTTP_201_CREATED)
async def create_evento(evento: EventoCreate, db: AsyncSession = Depends(get_db)):
    db_evento = Evento(**evento.dict())
    db.add(db_evento)
    await db.commit()
    await db.refresh(db_evento)
    return db_evento

@router.get("/", response_model=List[EventoOut])
async def list_eventos(
    skip: int = 0,
    limit: int = 500,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Evento).offset(skip).limit(limit).order_by(Evento.fecha_inicio.asc())
    )
    return result.scalars().all()

@router.get("/{evento_id}", response_model=EventoOut)
async def get_evento(evento_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Evento).where(Evento.id == evento_id))
    evento = result.scalar_one_or_none()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return evento

@router.put("/{evento_id}", response_model=EventoOut)
async def update_evento(evento_id: int, evento_data: EventoUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Evento).where(Evento.id == evento_id))
    evento = result.scalar_one_or_none()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    for key, value in evento_data.dict(exclude_unset=True).items():
        setattr(evento, key, value)
    await db.commit()
    await db.refresh(evento)
    return evento

@router.delete("/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evento(evento_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Evento).where(Evento.id == evento_id))
    evento = result.scalar_one_or_none()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    await db.delete(evento)
    await db.commit()
    return None
