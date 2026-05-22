from sqlalchemy import Column, Integer, String, DateTime, func
from app.models.base import Base

class ArchivoContrato(Base):
    __tablename__ = "archivos_contratos"

    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(Integer, nullable=False)
    nombre_original = Column(String, nullable=False)
    nombre_guardado = Column(String, nullable=False)
    ruta = Column(String, nullable=False)
    tipo = Column(String, nullable=True)
    tamanio = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
