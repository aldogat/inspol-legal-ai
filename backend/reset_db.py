import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.database import DATABASE_URL, Base
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.database import AsyncSessionLocal

async def reset():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    async with AsyncSessionLocal() as db:
        admin = User(email="admin@inspol.com", hashed_password=hash_password("admin123"), nombre="Admin", apellido="Principal", rol=UserRole.ADMIN)
        abogado = User(email="abogado@inspol.com", hashed_password=hash_password("abogado123"), nombre="Carlos", apellido="Gómez", rol=UserRole.ABOGADO)
        asistente = User(email="asistente@inspol.com", hashed_password=hash_password("asistente123"), nombre="María", apellido="López", rol=UserRole.ASISTENTE)
        db.add_all([admin, abogado, asistente])
        await db.commit()
    print("✅ BD reconstruida y usuarios creados.")

if __name__ == "__main__":
    asyncio.run(reset())
