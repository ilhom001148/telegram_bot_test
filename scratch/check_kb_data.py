import asyncio
from bot.db import SessionLocal
from bot.models import KnowledgeBase
from sqlalchemy import select

async def check_kb():
    async with SessionLocal() as db:
        result = await db.execute(select(KnowledgeBase).order_by(KnowledgeBase.id.desc()).limit(10))
        kb_items = result.scalars().all()
        for item in kb_items:
            print(f"ID: {item.id} | Q: {item.question[:50]} | A: {item.answer[:50]}")

if __name__ == "__main__":
    asyncio.run(check_kb())
