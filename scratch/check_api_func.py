import asyncio
import os
import sys

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.db import SessionLocal
from api.routes.dashboard import get_comprehensive_analytics

async def check():
    async with SessionLocal() as db:
        # get_comprehensive_analytics calls await db.scalar(...) etc.
        res = await get_comprehensive_analytics(db=db, period="1_week")
        print(res)

if __name__ == "__main__":
    asyncio.run(check())
