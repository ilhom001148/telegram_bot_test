import asyncio
from bot.db import SessionLocal
from bot.models import Message
from sqlalchemy import select

async def check_messages():
    async with SessionLocal() as db:
        result = await db.execute(select(Message).order_by(Message.id.desc()).limit(20))
        msgs = result.scalars().all()
        print(f"{'ID':<5} | {'From':<15} | {'Text':<30} | {'Is Q':<5} | {'Ans':<5}")
        print("-" * 70)
        for m in msgs:
            sender = m.full_name or m.username or "Unknown"
            text = (m.text or "").replace("\n", " ")[:30]
            print(f"{m.id:<5} | {sender:<15} | {text:<30} | {str(m.is_question):<5} | {str(m.is_answered):<5}")

if __name__ == "__main__":
    asyncio.run(check_messages())
