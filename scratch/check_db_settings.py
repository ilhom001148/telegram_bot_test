import asyncio
import os
from bot.db import SessionLocal
from bot.models import Setting

async def check_settings():
    async with SessionLocal() as db:
        try:
            from sqlalchemy import select
            result = await db.execute(select(Setting))
            settings = result.scalars().all()
            print("--- CURRENT SETTINGS ---")
            for s in settings:
                # Mask sensitive keys
                val = s.value
                if "key" in s.key:
                    val = val[:5] + "..." if val else "NONE"
                print(f"{s.key}: {val}")
            print("-------------------------")
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(check_settings())
