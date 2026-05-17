import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api.v1 import api_v1_router

# Carga las variables de entorno (incluyendo OPENAI_API_KEY)
load_dotenv()

app = FastAPI(title="IA Jurídica INSPOL")

# Configuración CORS para manejar correctamente las peticiones del navegador
app.add_middleware(
    CORSMiddleware,
    # Permite los orígenes de tu frontend en Render y localhost
    allow_origins=[
        "https://inspol-legal-ai-frontend.onrender.com",
        "https://inspol-legal-ai-final.onrender.com",
        "http://localhost:3000",
        "http://localhost:8000"
    ],
    # ⭐ PERMITE LOS MÉTODOS DE FORMA EXPLÍCITA ⭐
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Incluye las rutas de tu API
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"mensaje": "Backend funcionando correctamente"}
