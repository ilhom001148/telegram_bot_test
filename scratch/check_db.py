
import asyncio
from bot.db import SessionLocal
from bot.models import Message
from sqlalchemy import select, func

async def check_messages():
    async with SessionLocal() as db:
        result = await db.execute(select(func.count()).select_from(Message))
        count = result.scalar()
        print(f"Total messages in DB: {count}")
        
        # Check last 5 messages
        result = await db.execute(select(Message).order_by(Message.id.desc()).limit(5))
        msgs = result.scalars().all()
        for m in msgs:
            print(f"ID: {m.id}, Text: {m.text[:30]}, Created: {m.created_at}")

if __name__ == "__main__":
    asyncio.run(check_messages())
