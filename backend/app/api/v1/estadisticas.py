from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List
from datetime import date, timedelta, datetime
from pydantic import BaseModel

from app.database import get_db
from app.models.expediente import Expediente
from app.models.cliente import Cliente
from app.models.contrato import Contrato
from app.models.transaccion import Transaccion
from app.models.evento import Evento

router = APIRouter()

class EstadisticasOut(BaseModel):
    casos_activos: int = 0
    casos_cerrados: int = 0
    total_clientes: int = 0
    total_contratos: int = 0
    contratos_por_vencer: int = 0
    total_ingresos: float = 0.0
    total_gastos: float = 0.0
    balance: float = 0.0
    total_transacciones: int = 0
    eventos_proximos: List[dict] = []
    expedientes_activos: List[dict] = []
    productividad_semanal: List[dict] = []
    casos_por_area: List[dict] = []
    ahorro_ia: List[dict] = []

@router.get("/")
async def obtener_estadisticas(db: AsyncSession = Depends(get_db)):
    try:
        hoy = date.today()
        activos = await db.scalar(select(func.count(Expediente.id)).where(Expediente.estado == "Activo")) or 0
        cerrados = await db.scalar(select(func.count(Expediente.id)).where(Expediente.estado == "Cerrado")) or 0
        total_clientes = await db.scalar(select(func.count(Cliente.id))) or 0
        total_contratos = await db.scalar(select(func.count(Contrato.id))) or 0
        limite = hoy + timedelta(days=30)
        contratos_por_vencer = await db.scalar(
            select(func.count(Contrato.id)).where(and_(Contrato.fecha_vencimiento <= limite, Contrato.fecha_vencimiento >= hoy, Contrato.estado == "Activo"))
        ) or 0
        total_ingresos = await db.scalar(select(func.coalesce(func.sum(Transaccion.monto), 0)).where(Transaccion.tipo == "Ingreso")) or 0.0
        total_gastos = await db.scalar(select(func.coalesce(func.sum(Transaccion.monto), 0)).where(Transaccion.tipo == "Gasto")) or 0.0
        balance = total_ingresos - total_gastos
        total_transacciones = await db.scalar(select(func.count(Transaccion.id))) or 0

        eventos_query = await db.execute(select(Evento).where(Evento.fecha_inicio >= hoy).order_by(Evento.fecha_inicio.asc()).limit(5))
        eventos = eventos_query.scalars().all()
        eventos_proximos = [{"id": ev.id, "titulo": ev.titulo, "fecha_inicio": ev.fecha_inicio.isoformat(), "tipo": ev.tipo, "color": ev.color, "ubicacion": ev.ubicacion} for ev in eventos]

        exp_query = await db.execute(select(Expediente).where(Expediente.estado == "Activo").order_by(Expediente.fecha_apertura.desc()).limit(10))
        expedientes = exp_query.scalars().all()
        expedientes_activos = [{"id": e.id, "numero_expediente": e.numero_expediente, "cliente": e.cliente, "estado": e.estado, "prioridad": e.prioridad, "fecha_apertura": e.fecha_apertura.isoformat() if e.fecha_apertura else None} for e in expedientes]

        productividad_semanal = []
        for i in range(6, -1, -1):
            dia = hoy - timedelta(days=i)
            count = await db.scalar(select(func.count(Expediente.id)).where(func.date(Expediente.created_at) == dia)) or 0
            productividad_semanal.append({"day": dia.strftime("%a").capitalize() if i > 0 else "Hoy", "value": count})

        casos_por_area = []
        for prioridad in ["Alta", "Media", "Baja"]:
            count = await db.scalar(select(func.count(Expediente.id)).where(Expediente.prioridad == prioridad)) or 0
            casos_por_area.append({"name": prioridad, "value": count})

        ahorro_ia = [{"month": f"Sem{s+1}", "value": 0} for s in range(4)]

        return {
            "casos_activos": activos, "casos_cerrados": cerrados, "total_clientes": total_clientes,
            "total_contratos": total_contratos, "contratos_por_vencer": contratos_por_vencer,
            "total_ingresos": total_ingresos, "total_gastos": total_gastos, "balance": balance,
            "total_transacciones": total_transacciones, "eventos_proximos": eventos_proximos,
            "expedientes_activos": expedientes_activos, "productividad_semanal": productividad_semanal,
            "casos_por_area": casos_por_area, "ahorro_ia": ahorro_ia
        }
    except Exception as e:
        print(f"ERROR en estadisticas: {e}")
        return {
            "casos_activos": 0, "casos_cerrados": 0, "total_clientes": 0, "total_contratos": 0,
            "contratos_por_vencer": 0, "total_ingresos": 0, "total_gastos": 0, "balance": 0,
            "total_transacciones": 0, "eventos_proximos": [], "expedientes_activos": [],
            "productividad_semanal": [], "casos_por_area": [], "ahorro_ia": []
        }
