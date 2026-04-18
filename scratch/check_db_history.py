import asyncio
from api.dependencies import get_db
from bot.models import Group, Message
from sqlalchemy import select, func

async def check_db():
    print("Checking database...")
    async for db in get_db():
        # Get all groups
        g_res = await db.execute(select(Group.id, Group.title, Group.telegram_id))
        groups = g_res.all()
        print(f"Total groups: {len(groups)}")
        for g in groups:
            m_res = await db.execute(select(func.count(Message.id)).filter(Message.group_id == g.id))
            m_count = m_res.scalar()
            print(f"Group ID: {g.id}, Title: {g.title}, Telegram ID: {g.telegram_id}, Messages: {m_count}")
        
        # Get total messages
        all_m_res = await db.execute(select(func.count(Message.id)))
        print(f"Total messages in DB: {all_m_res.scalar()}")

if __name__ == "__main__":
    asyncio.run(check_db())
