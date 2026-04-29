import asyncio
from bot.db import engine
from sqlalchemy import text

async def check():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'messages'"))
        for row in res:
            print(f"{row[0]}: {row[1]}")

if __name__ == "__main__":
    asyncio.run(check())
