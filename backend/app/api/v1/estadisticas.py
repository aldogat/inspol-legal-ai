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

class GraficaLinea(BaseModel):
    day: str
    value: int

class GraficaTorta(BaseModel):
    name: str
    value: int

class GraficaBarra(BaseModel):
    month: str
    value: int

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
    productividad_semanal: List[GraficaLinea] = []
    casos_por_area: List[GraficaTorta] = []
    ahorro_ia: List[GraficaBarra] = []

@router.get("/")
async def obtener_estadisticas(db: AsyncSession = Depends(get_db)):
    hoy = date.today()
    try:
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

        # Eventos próximos
        eventos_query = await db.execute(select(Evento).where(Evento.fecha_inicio >= hoy).order_by(Evento.fecha_inicio.asc()).limit(5))
        eventos = eventos_query.scalars().all()
        eventos_proximos = [{"id": ev.id, "titulo": ev.titulo, "fecha_inicio": ev.fecha_inicio.isoformat(), "tipo": ev.tipo, "color": ev.color, "ubicacion": ev.ubicacion} for ev in eventos]

        # Expedientes activos
        exp_query = await db.execute(select(Expediente).where(Expediente.estado == "Activo").order_by(Expediente.fecha_apertura.desc()).limit(10))
        expedientes = exp_query.scalars().all()
        expedientes_activos = [{"id": e.id, "numero_expediente": e.numero_expediente, "cliente": e.cliente, "estado": e.estado, "prioridad": e.prioridad, "fecha_apertura": e.fecha_apertura.isoformat() if e.fecha_apertura else None} for e in expedientes]

        # Productividad Semanal: basada en fecha_apertura de los últimos 7 días
        productividad_semanal = []
        for i in range(6, -1, -1):
            dia = hoy - timedelta(days=i)
            count = await db.scalar(select(func.count(Expediente.id)).where(Expediente.fecha_apertura == dia)) or 0
            productividad_semanal.append({"day": dia.strftime("%a").capitalize() if i > 0 else "Hoy", "value": count})

        # Casos por prioridad
        prioridades = ["Alta", "Media", "Baja"]
        casos_por_area = []
        for prioridad in prioridades:
            count = await db.scalar(select(func.count(Expediente.id)).where(Expediente.prioridad == prioridad)) or 0
            casos_por_area.append({"name": prioridad, "value": count})

        # Ingresos Mensuales: sumar transacciones "Ingreso" de las últimas 4 semanas (lunes a domingo)
        ahorro_ia = []
        # Calcular el inicio de la semana actual (lunes)
        inicio_semana_actual = hoy - timedelta(days=hoy.weekday())
        for semana in range(4):
            inicio = inicio_semana_actual - timedelta(weeks=3-semana)
            fin = inicio + timedelta(days=6)
            total_semana = await db.scalar(
                select(func.coalesce(func.sum(Transaccion.monto), 0)).where(
                    and_(
                        Transaccion.tipo == "Ingreso",
                        Transaccion.fecha >= datetime(inicio.year, inicio.month, inicio.day),
                        Transaccion.fecha <= datetime(fin.year, fin.month, fin.day, 23, 59, 59)
                    )
                )
            ) or 0.0
            ahorro_ia.append({"month": f"Sem{semana+1}", "value": int(total_semana)})

        return {
            "casos_activos": activos, "casos_cerrados": cerrados,
            "total_clientes": total_clientes, "total_contratos": total_contratos,
            "contratos_por_vencer": contratos_por_vencer,
            "total_ingresos": total_ingresos, "total_gastos": total_gastos,
            "balance": balance, "total_transacciones": total_transacciones,
            "eventos_proximos": eventos_proximos, "expedientes_activos": expedientes_activos,
            "productividad_semanal": productividad_semanal,
            "casos_por_area": casos_por_area,
            "ahorro_ia": ahorro_ia,
        }
    except Exception as e:
        print(f"ERROR en estadisticas: {e}")
        return {
            "casos_activos": 0, "casos_cerrados": 0, "total_clientes": 0, "total_contratos": 0,
            "contratos_por_vencer": 0, "total_ingresos": 0, "total_gastos": 0, "balance": 0,
            "total_transacciones": 0, "eventos_proximos": [], "expedientes_activos": [],
            "productividad_semanal": [], "casos_por_area": [], "ahorro_ia": []
        }
