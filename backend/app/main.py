import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.database import engine
from app.models.base import Base
from app.api.v1 import chat, expedientes, clientes, contratos, eventos, finanzas, reportes, auth, estadisticas, archivos, documentos, archivos_contratos, historial, analisis

load_dotenv()
app = FastAPI(title="INSPOL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(expedientes.router, prefix="/api/v1/expedientes", tags=["expedientes"])
app.include_router(clientes.router, prefix="/api/v1/clientes", tags=["clientes"])
app.include_router(contratos.router, prefix="/api/v1/contratos", tags=["contratos"])
app.include_router(eventos.router, prefix="/api/v1/eventos", tags=["eventos"])
app.include_router(finanzas.router, prefix="/api/v1/finanzas", tags=["finanzas"])
app.include_router(reportes.router, prefix="/api/v1/reportes", tags=["reportes"])
app.include_router(estadisticas.router, prefix="/api/v1/estadisticas", tags=["estadisticas"])
app.include_router(archivos.router, prefix="/api/v1", tags=["archivos"])
app.include_router(documentos.router, prefix="/api/v1/documentos", tags=["documentos"])
app.include_router(archivos_contratos.router, prefix="/api/v1", tags=["archivos-contratos"])
app.include_router(historial.router, prefix="/api/v1/historial", tags=["historial"])
app.include_router(analisis.router, prefix="/api/v1/analisis", tags=["analisis"])

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"mensaje":"Backend OK"}
