import asyncio
from bot.db import SessionLocal
from bot.models import Group, Message
from sqlalchemy import select, func

async def main():
    async with SessionLocal() as db:
        result = await db.execute(select(Group))
        groups = result.scalars().all()
        print(f"Total groups found: {len(groups)}")
        for g in groups:
            print(f"ID: {g.id} | Title: '{g.title}' | Telegram ID: {g.telegram_id}")
            
        m_result = await db.execute(select(func.count(Message.id)))
        m_count = m_result.scalar()
        print(f"Total messages found: {m_count}")

if __name__ == "__main__":
    asyncio.run(main())
