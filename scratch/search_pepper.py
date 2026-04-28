import asyncio
from bot.db import SessionLocal
from bot.models import Message
from sqlalchemy import select

async def search_pepper():
    async with SessionLocal() as db:
        result = await db.execute(select(Message).filter(Message.text.contains("🌶️")))
        msgs = result.scalars().all()
        for m in msgs:
            print(f"ID: {m.id} | From: {m.full_name} | Text: {m.text} | Time: {m.created_at}")

if __name__ == "__main__":
    asyncio.run(search_pepper())
