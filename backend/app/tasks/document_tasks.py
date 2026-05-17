from app.core.celery_app import celery_app
from app.services.ai_engine import analyze_contract

@celery_app.task
def analyze_document_task(document_id: str, text: str, tenant_id: str):
    analysis = analyze_contract(text, tenant_id)
    return {"document_id": document_id, "analysis": analysis}
