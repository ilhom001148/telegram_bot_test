import asyncio
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Assuming bot/models.py exists and contains Message model
from bot.models import Message

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "telegram_ai")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async def check_recent_activity():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        result = await session.execute(select(Message).order_by(Message.id.desc()).limit(10))
        messages = result.scalars().all()
        
        if not messages:
            print("No messages found in database.")
            return

        print(f"Found {len(messages)} recent messages:")
        for m in messages:
            print(f"ID: {m.id} | Date: {m.created_at} | User: {m.full_name} | Text: {m.text[:50]}...")

if __name__ == "__main__":
    asyncio.run(check_recent_activity())
