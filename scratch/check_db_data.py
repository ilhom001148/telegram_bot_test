import sys
import os
sys.path.append(os.getcwd())
import asyncio
import os
from sqlalchemy import select, func
from bot.db import SessionLocal, engine
from bot.models import Group, Message

async def check_data():
    async with SessionLocal() as db:
        # Check groups
        groups_res = await db.execute(select(Group))
        groups = groups_res.scalars().all()
        print(f"Total Groups: {len(groups)}")
        for g in groups:
            msg_count_res = await db.execute(select(func.count(Message.id)).filter(Message.group_id == g.id))
            msg_count = msg_count_res.scalar()
            print(f"Group: '{g.title}' (ID: {g.id}, TG_ID: {g.telegram_id}) - Messages: {msg_count}")
        
        # Total messages
        total_msg_res = await db.execute(select(func.count(Message.id)))
        total_msg = total_msg_res.scalar()
        print(f"Total Messages in DB: {total_msg}")

if __name__ == "__main__":
    asyncio.run(check_data())
