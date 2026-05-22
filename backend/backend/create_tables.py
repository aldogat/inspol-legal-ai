import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.base import Base
from app.models.user import User
from app.models.expediente import Expediente
import os
from dotenv import load_dotenv

async def init():
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init())
