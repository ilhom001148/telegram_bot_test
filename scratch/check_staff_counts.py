import asyncio
from bot.db import SessionLocal
from bot.models import Message
from sqlalchemy import select, func

async def check():
    async with SessionLocal() as db:
        res = await db.execute(select(Message.is_staff, func.count(Message.id)).group_by(Message.is_staff))
        rows = res.all()
        for row in rows:
            print(f"is_staff={row[0]}: {row[1]}")

if __name__ == "__main__":
    asyncio.run(check())
