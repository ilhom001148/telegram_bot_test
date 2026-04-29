import asyncio
from bot.db import SessionLocal
from bot.models import ProcessedUpdate
from sqlalchemy import select, func

async def check_processed_updates():
    async with SessionLocal() as db:
        count = await db.scalar(select(func.count(ProcessedUpdate.update_id)))
        latest = await db.execute(select(ProcessedUpdate).order_by(ProcessedUpdate.processed_at.desc()).limit(5))
        latest_rows = latest.scalars().all()
        
        print(f"Total processed updates: {count}")
        print("Latest processed updates:")
        for up in latest_rows:
            print(f"ID: {up.update_id}, Processed at: {up.processed_at}")

if __name__ == "__main__":
    asyncio.run(check_processed_updates())
