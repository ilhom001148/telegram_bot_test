import asyncio
from bot.db import SessionLocal
from bot.models import Message
from sqlalchemy import select

async def check():
    async with SessionLocal() as db:
        res = await db.execute(select(Message.created_at, Message.answered_at).where(Message.answered_at != None).limit(5))
        rows = res.all()
        for row in rows:
            print(f"created_at: {row[0]} (tzinfo: {row[0].tzinfo if row[0] else 'N/A'})")
            print(f"answered_at: {row[1]} (tzinfo: {row[1].tzinfo if row[1] else 'N/A'})")

if __name__ == "__main__":
    asyncio.run(check())
