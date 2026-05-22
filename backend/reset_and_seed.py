import asyncio
from app.database import engine, Base
from app.models.user import User, UserRole
from app.core.security import hash_password
from sqlalchemy import select

async def reset_and_seed():
    # Borrar todas las tablas y recrearlas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # Insertar usuarios
    async with engine.begin() as conn:
        # Usamos una sesión normal para insertar
        from sqlalchemy.orm import Session
        # No, engine.begin() es conexión, usamos sessionmaker síncrona? Mejor async session
        # Vamos a usar get_db()
        pass

# Mejor implementación con AsyncSession
async def seed_users():
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(User).where(User.email == "admin@inspol.com"))
        if not existing.scalars().first():
            admin = User(email="admin@inspol.com", hashed_password=hash_password("admin123"), nombre="Admin", apellido="Principal", rol=UserRole.ADMIN)
            abogado = User(email="abogado@inspol.com", hashed_password=hash_password("abogado123"), nombre="Carlos", apellido="Gómez", rol=UserRole.ABOGADO)
            asistente = User(email="asistente@inspol.com", hashed_password=hash_password("asistente123"), nombre="María", apellido="López", rol=UserRole.ASISTENTE)
            db.add_all([admin, abogado, asistente])
            await db.commit()
            print("✅ Usuarios creados: admin@inspol.com / admin123, abogado@inspol.com / abogado123, asistente@inspol.com / asistente123")
        else:
            print("ℹ️ Los usuarios ya existen")

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await seed_users()

if __name__ == "__main__":
    asyncio.run(main())
