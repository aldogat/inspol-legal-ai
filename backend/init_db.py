import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.user import Base
import os
from dotenv import load_dotenv

async def init():
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL no está definida en el archivo .env")
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init())
