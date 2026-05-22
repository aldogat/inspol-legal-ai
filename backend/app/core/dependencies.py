from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import UserRole

REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Token requerido")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        rol = payload.get("rol")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return {"email": email, "rol": rol}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

async def get_current_user_or_anon(credentials: HTTPAuthorizationCredentials = Security(security_scheme)):
    if REQUIRE_AUTH:
        if not credentials:
            raise HTTPException(status_code=401, detail="Token requerido")
        return await get_current_user(credentials)
    else:
        if credentials:
            try:
                return await get_current_user(credentials)
            except HTTPException:
                pass
        return {"email": "anon", "rol": "admin"}

def require_role(required_roles: list[UserRole]):
    async def role_checker(current_user: dict = Depends(get_current_user_or_anon)):
        if current_user["rol"] not in [r.value for r in required_roles]:
            raise HTTPException(status_code=403, detail="No tienes permiso")
        return current_user
    return role_checker
