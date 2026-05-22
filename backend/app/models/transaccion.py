from sqlalchemy import Column, Integer, String, Float, DateTime, Text, func
from app.models.base import Base

class Transaccion(Base):
    __tablename__ = "transacciones"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)  # "Ingreso" o "Gasto"
    categoria = Column(String, nullable=False)  # Honorarios, Alquiler, etc.
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime(timezone=True), nullable=False)
    descripcion = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
