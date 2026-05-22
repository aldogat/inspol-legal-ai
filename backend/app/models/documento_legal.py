from sqlalchemy import Column, Integer, String, Text, DateTime, func
from pgvector.sqlalchemy import Vector
from app.models.base import Base

class DocumentoLegal(Base):
    __tablename__ = "documentos_legales"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    contenido = Column(Text, nullable=False)
    embedding = Column(Vector(384))
    fuente = Column(String, nullable=True)
    articulo = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
