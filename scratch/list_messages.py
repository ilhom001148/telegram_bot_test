import asyncio
from bot.db import SessionLocal
from bot.models import Message
from sqlalchemy import select

async def check():
    async with SessionLocal() as db:
        res = await db.execute(select(Message.text).order_by(Message.id.desc()).limit(50))
        rows = res.all()
        for row in rows:
            print(f"- {row[0]}")

if __name__ == "__main__":
    asyncio.run(check())
