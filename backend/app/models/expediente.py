from sqlalchemy import Column, Integer, String, Date, Text, DateTime, func
from app.models.base import Base  # <-- CORRECCIÓN

class Expediente(Base):
    __tablename__ = "expedientes"

    id = Column(Integer, primary_key=True, index=True)
    numero_expediente = Column(String, unique=True, index=True, nullable=False)
    cliente = Column(String, nullable=False)
    juzgado = Column(String, nullable=True)
    estado = Column(String, default="Activo")
    prioridad = Column(String, default="Media")
    descripcion = Column(Text, nullable=True)
    fecha_apertura = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
