from sqlalchemy import Column, Integer, String, DateTime, Text, func
from app.models.base import Base

class HistorialExpediente(Base):
    __tablename__ = "historial_expedientes"
    id = Column(Integer, primary_key=True, index=True)
    expediente_id = Column(Integer, nullable=False)
    numero_expediente = Column(String, nullable=False)
    accion = Column(String, nullable=False)  # creado, editado, eliminado
    descripcion = Column(Text, nullable=True)
    usuario_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class HistorialContrato(Base):
    __tablename__ = "historial_contratos"
    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(Integer, nullable=False)
    numero_contrato = Column(String, nullable=False)
    accion = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    usuario_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
