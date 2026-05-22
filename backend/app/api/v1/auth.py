from fastapi import APIRouter
router = APIRouter()

@router.post("/login")
async def login():
    return {"message": "Login no implementado - modo sin autenticación"}

@router.post("/register")
async def register():
    return {"message": "Register no implementado - modo sin autenticación"}
