import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func, text

# Get DATABASE_URL from env or bot/db.py logic
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

async def diag():
    if not DATABASE_URL:
        print("DATABASE_URL not found!")
        return
    
    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check Groups
        print("\n--- Groups ---")
        res = await session.execute(text("SELECT id, title, telegram_id FROM groups"))
        groups = res.all()
        for g in groups:
            msg_res = await session.execute(text(f"SELECT count(*) FROM messages WHERE group_id = {g[0]}"))
            count = msg_res.scalar()
            print(f"ID: {g[0]} | Title: '{g[1]}' | Telegram ID: {g[2]} | Messages: {count}")
        
        # Check Messages with no group
        print("\n--- Messages with no group ---")
        res = await session.execute(text("SELECT count(*) FROM messages WHERE group_id IS NULL"))
        print(f"Count: {res.scalar()}")
        
        # Check Total Messages
        print("\n--- Total Messages ---")
        res = await session.execute(text("SELECT count(*) FROM messages"))
        print(f"Count: {res.scalar()}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(diag())
