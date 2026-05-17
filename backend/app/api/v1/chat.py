from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

router = APIRouter()

# Pydantic model for the request body
class ChatRequest(BaseModel):
    consulta: str

@router.post("/multimodal")
async def multimodal_chat(request: ChatRequest):
    # Initialize the OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente legal experto en derecho."},
                {"role": "user", "content": request.consulta}
            ],
            temperature=0.7,
            max_tokens=800
        )
        # Extract the answer
        answer = response.choices[0].message.content
        return {"respuesta": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
