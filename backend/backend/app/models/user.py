import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ABOGADO = "abogado"
    ASISTENTE = "asistente"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    rol = Column(Enum(UserRole), default=UserRole.ASISTENTE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
