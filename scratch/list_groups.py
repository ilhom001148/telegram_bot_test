import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot.db import SessionLocal
from bot.models import Group
from sqlalchemy import select

async def list_groups():
    async with SessionLocal() as db:
        result = await db.execute(select(Group))
        groups = result.scalars().all()
        for g in groups:
            print(f"Title: {g.title}, ID: {g.telegram_id}")

if __name__ == "__main__":
    asyncio.run(list_groups())
