from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from app.models.base import Base

class Conversacion(Base):
    __tablename__ = "conversaciones"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rol = Column(String, nullable=False)  # "user" o "assistant"
    contenido = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
