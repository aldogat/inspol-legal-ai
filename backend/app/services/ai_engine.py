import json
from openai import AsyncOpenAI
from app.core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def analyze_contract(text: str, context: str = None) -> dict:
    system_prompt = """Eres un abogado experto en revisión contractual. Analiza el contrato y devuelve un JSON con:
    - risk_score: número 0-100
    - traffic_light: "green" (0-30), "yellow" (31-60), "red" (61-100)
    - summary: resumen ejecutivo
    - risks: lista de objetos {clause, risk, severity, suggestion}
    - missing_clauses: lista de cláusulas que deberían incluirse
    """
    user_content = text
    if context:
        user_content = f"Contexto: {context}\n\nContrato: {text}"
    
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    return json.loads(response.choices[0].message.content)
