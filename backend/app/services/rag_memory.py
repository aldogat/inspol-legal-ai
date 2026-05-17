import weaviate
from datetime import datetime
from app.core.config import settings
from openai import AsyncOpenAI

# Conexión compatible con Weaviate v4
try:
    # Método recomendado para instancias locales (v4)
    weaviate_client = weaviate.connect_to_local()
except Exception:
    try:
        # Alternativa con ConnectionParams (v4)
        weaviate_client = weaviate.WeaviateClient(
            connection_params=weaviate.ConnectionParams.from_url(
                url=settings.WEAVIATE_URL,
                grpc_port=50051
            )
        )
        weaviate_client.connect()
    except Exception:
        # Si nada funciona, el chat funcionará sin memoria RAG
        weaviate_client = None

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class LegalMemory:
    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id

    async def _embed(self, text: str):
        resp = await openai_client.embeddings.create(model="text-embedding-3-small", input=text)
        return resp.data[0].embedding

    async def store_interaction(self, question: str, answer: str, metadata: dict = None):
        if not weaviate_client: return
        embedding = await self._embed(question)
        weaviate_client.collections.get("LegalMemory").data.insert(
            properties={
                "tenant_id": self.tenant_id,
                "type": "interaction",
                "question": question,
                "answer": answer,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            },
            vector=embedding
        )

    async def store_case_metric(self, case_data: dict):
        if not weaviate_client: return
        embedding = await self._embed(case_data.get("title", ""))
        weaviate_client.collections.get("LegalMemory").data.insert(
            properties={
                "tenant_id": self.tenant_id,
                "type": "case_metric",
                "title": case_data.get("title"),
                "action": case_data.get("action"),
                "time_saved_minutes": case_data.get("time_saved", 0),
                "money_saved_estimate": case_data.get("money_saved", 0),
                "result": case_data.get("result", "pendiente"),
                "timestamp": datetime.utcnow().isoformat()
            },
            vector=embedding
        )

    async def retrieve_similar(self, query: str, limit: int = 3) -> list:
        if not weaviate_client: return []
        embedding = await self._embed(query)
        result = weaviate_client.collections.get("LegalMemory").query.near_vector(
            near_vector=embedding,
            limit=limit,
            return_properties=["question", "answer", "correction"]
        )
        return [obj.properties for obj in result.objects]

async def get_memory(tenant_id: str = "default") -> LegalMemory:
    return LegalMemory(tenant_id)
