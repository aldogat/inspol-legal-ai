import asyncio
from app.database import engine, Base, get_db
from app.models.user import User, UserRole
from app.core.security import hash_password
from sqlalchemy import select

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with get_db() as db:
        existing = await db.execute(select(User).where(User.email == "admin@inspol.com"))
        if not existing.scalars().first():
            admin = User(
                email="admin@inspol.com",
                hashed_password=hash_password("admin123"),
                nombre="Admin",
                apellido="Principal",
                rol=UserRole.ADMIN
            )
            abogado = User(
                email="abogado@inspol.com",
                hashed_password=hash_password("abogado123"),
                nombre="Carlos",
                apellido="Gómez",
                rol=UserRole.ABOGADO
            )
            asistente = User(
                email="asistente@inspol.com",
                hashed_password=hash_password("asistente123"),
                nombre="María",
                apellido="López",
                rol=UserRole.ASISTENTE
            )
            db.add_all([admin, abogado, asistente])
            await db.commit()
            print("Usuarios creados: admin@inspol.com / admin123, abogado@inspol.com / abogado123, asistente@inspol.com / asistente123")
        else:
            print("Usuarios ya existen")

if __name__ == "__main__":
    asyncio.run(seed())
