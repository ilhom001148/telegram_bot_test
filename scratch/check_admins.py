import asyncio
import os
from sqlalchemy import select, func
from bot.db import engine, SessionLocal
from bot.models import Admin

async def check():
    async with SessionLocal() as db:
        try:
            result = await db.execute(select(Admin))
            admins = result.scalars().all()
            print(f"Found {len(admins)} admins:")
            for a in admins:
                print(f" - ID: {a.id}, Username: {a.username}")
        except Exception as e:
            print(f"Error checking admins: {e}")
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(check())
