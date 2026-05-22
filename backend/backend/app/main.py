import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api.v1 import auth  # importamos auth
from app.api.v1 import chat as chat_router  # si ya lo tienes

load_dotenv()

app = FastAPI(title="IA Jurídica INSPOL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://inspol-legal-ai-frontend.onrender.com",
        "http://localhost:3000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# si ya tenías el de chat, lo mantienes, por ejemplo:
# app.include_router(chat_router.router, prefix="/api/v1/chat", tags=["chat"])

@app.get("/")
def root():
    return {"mensaje": "Backend funcionando correctamente"}
