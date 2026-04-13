import asyncio
import os
from sqlalchemy import func, select
from bot.db import engine, SessionLocal
from bot.models import Group, Message

async def check_stats_empty():
    async with SessionLocal() as db:
        try:
            print("Checking groups count (filtered for non-existent)...")
            total_groups_result = await db.execute(select(func.count(Group.id)).filter(Group.id == 0))
            print(f"Groups: {total_groups_result.scalar()}")
            
            print("Checking most active group (empty join)...")
            query = (
                select(Group.title, func.count(Message.id))
                .join(Message, Group.id == Message.group_id)
                .filter(Group.id == 0)
                .group_by(Group.id, Group.title)
            )
            res = await db.execute(query)
            raw = res.first()
            print(f"Raw: {raw}")
            if raw:
                print(f"Title: {raw[0]}")
            else:
                print("No data found as expected.")
                
            print("Checking specific column access on empty result...")
            # This is where a common error happens: trying to Access g[0] on None
            
            print("Success!")
        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(check_stats_empty())
