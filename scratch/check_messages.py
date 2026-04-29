import asyncio
from bot.db import SessionLocal
from bot.models import Message, Group
from sqlalchemy import select

async def check_recent_messages():
    async with SessionLocal() as db:
        stmt = select(Message, Group).join(Group, Message.group_id == Group.id).order_by(Message.id.desc()).limit(10)
        result = await db.execute(stmt)
        rows = result.all()
        
        print(f"{'ID':<5} | {'Text':<20} | {'Is_Q':<5} | {'Is_A':<5} | {'Is_Staff':<8} | {'Group':<15}")
        print("-" * 70)
        for msg, grp in rows:
            text = (msg.text or "")[:20].replace('\n', ' ')
            print(f"{msg.id:<5} | {text:<20} | {msg.is_question:<5} | {msg.is_answered:<5} | {msg.is_staff:<8} | {grp.title[:15]}")

if __name__ == "__main__":
    asyncio.run(check_recent_messages())
