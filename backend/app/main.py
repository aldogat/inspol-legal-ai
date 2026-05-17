import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="IA Jurídica INSPOL")

# Configuración CORS - Permitir solicitudes de tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://inspol-legal-ai-final.onrender.com",
        "https://inspol-legal-ai-frontend.onrender.com",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar cliente de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Consulta(BaseModel):
    consulta: str

@app.get("/")
def root():
    return {"mensaje": "Backend funcionando correctamente"}

@app.post("/api/v1/chat/multimodal")
def chat(consulta: Consulta):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un abogado experto en derecho ecuatoriano."},
                {"role": "user", "content": consulta.consulta}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return {"respuesta": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
