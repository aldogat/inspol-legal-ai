from pydantic import BaseModel

class ContractAnalysisRequest(BaseModel):
    text: str
    context: str = None
