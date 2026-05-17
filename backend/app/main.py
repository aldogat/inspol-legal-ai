import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api.v1 import api_v1_router

load_dotenv()

app = FastAPI(title="IA Jurídica INSPOL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://inspol-legal-ai-final.onrender.com",
        "https://inspol-legal-ai-frontend.onrender.com",
        "http://localhost:3000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"mensaje": "Backend funcionando correctamente"}
