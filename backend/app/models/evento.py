from sqlalchemy import Column, Integer, String, DateTime, Text, func
from app.models.base import Base

class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)
    fecha_fin = Column(DateTime(timezone=True), nullable=False)
    tipo = Column(String, default="Reunión")  # Audiencia, Reunión, Plazo, Otro
    ubicacion = Column(String, nullable=True)
    color = Column(String, default="#3b82f6")  # Color en hex para el calendario
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
