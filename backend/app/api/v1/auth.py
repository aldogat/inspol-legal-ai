from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.security import create_access_token
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/login")
async def login(username: str, password: str):
    # demo: cualquier login funciona
    token = create_access_token({"sub": "demo", "email": username})
    return {"access_token": token, "token_type": "bearer"}
