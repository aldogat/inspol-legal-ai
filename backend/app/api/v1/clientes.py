from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.cliente import Cliente

router = APIRouter()

class ClienteCreate(BaseModel):
    nombre: str
    email: str
    telefono: Optional[str] = None
    rfc: Optional[str] = None
    direccion: Optional[str] = None

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    rfc: Optional[str] = None
    direccion: Optional[str] = None

class ClienteOut(BaseModel):
    id: int
    nombre: str
    email: str
    telefono: Optional[str]
    rfc: Optional[str]
    direccion: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    class Config:
        from_attributes = True

@router.post("/", response_model=ClienteOut, status_code=201)
async def crear(cli: ClienteCreate, db: AsyncSession = Depends(get_db)):
    if (await db.execute(select(Cliente).where(Cliente.email == cli.email))).scalar_one_or_none():
        raise HTTPException(400, "Email ya registrado")
    nuevo = Cliente(**cli.dict())
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=List[ClienteOut])
async def listar(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Cliente).order_by(Cliente.id).offset(skip).limit(limit))
    return r.scalars().all()

@router.get("/{cliente_id}", response_model=ClienteOut)
async def obtener(cliente_id: int, db: AsyncSession = Depends(get_db)):
    c = await db.get(Cliente, cliente_id)
    if not c: raise HTTPException(404)
    return c

@router.put("/{cliente_id}", response_model=ClienteOut)
async def actualizar(cliente_id: int, cli_data: ClienteUpdate, db: AsyncSession = Depends(get_db)):
    c = await db.get(Cliente, cliente_id)
    if not c: raise HTTPException(404)
    for k, v in cli_data.dict(exclude_unset=True).items():
        setattr(c, k, v)
    await db.commit()
    await db.refresh(c)
    return c

@router.delete("/{cliente_id}", status_code=204)
async def eliminar(cliente_id: int, db: AsyncSession = Depends(get_db)):
    c = await db.get(Cliente, cliente_id)
    if not c: raise HTTPException(404)
    await db.delete(c)
    await db.commit()
