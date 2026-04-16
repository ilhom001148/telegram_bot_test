import asyncio
from bot.db import SessionLocal
from bot.models import Setting, Message
from sqlalchemy import select, func

async def check_all():
    async with SessionLocal() as db:
        print("=== SETTINGS ===")
        res = await db.execute(select(Setting))
        settings = res.scalars().all()
        if not settings:
            print("No settings found in DB.")
        for s in settings:
            print(f"Key: {s.key}, Value: {s.value[:100]}...")
            
        print("\n=== MESSAGE STATS ===")
        res = await db.execute(select(func.count(Message.id)))
        print(f"Total messages: {res.scalar()}")
        
        print("\n=== RECENT MESSAGES ===")
        res = await db.execute(select(Message).order_by(Message.id.desc()).limit(5))
        for m in res.scalars():
            print(f"ID: {m.id}, Text: {m.text[:50]}, IsQuestion: {m.is_question}, IsStaff: {m.is_staff}")

if __name__ == "__main__":
    asyncio.run(check_all())
