import asyncio
from bot.db import SessionLocal
from bot.models import KnowledgeBase, Company, Setting
from sqlalchemy import select, func

async def check_data():
    print("--- Database Content Check ---")
    async with SessionLocal() as db:
        # KnowledgeBase
        kb_res = await db.execute(select(func.count(KnowledgeBase.id)))
        kb_count = kb_res.scalar()
        print(f"KnowledgeBase entries: {kb_count}")
        if kb_count > 0:
            items = await db.execute(select(KnowledgeBase).limit(3))
            for item in items.scalars():
                print(f"  - Q: {item.question[:50]}... | A: {item.answer[:50]}...")

        # Companies
        comp_res = await db.execute(select(func.count(Company.id)))
        comp_count = comp_res.scalar()
        print(f"Company entries: {comp_count}")
        if comp_count > 0:
            items = await db.execute(select(Company).limit(3))
            for item in items.scalars():
                print(f"  - Name: {item.name} | Phone: {item.phone}")

        # Settings
        set_res = await db.execute(select(Setting))
        settings = set_res.scalars().all()
        print(f"Settings entries: {len(settings)}")
        for s in settings:
            print(f"  - {s.key}: {str(s.value)[:100]}...")

if __name__ == "__main__":
    asyncio.run(check_data())
