import asyncio
from sqlalchemy import select
from bot.db import SessionLocal
from bot.models import Company

async def check():
    async with SessionLocal() as db:
        res = await db.execute(select(Company))
        print("DB Count:", len(res.scalars().all()))

if __name__ == '__main__':
    asyncio.run(check())
