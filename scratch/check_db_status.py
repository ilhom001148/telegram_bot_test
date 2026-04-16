import asyncio
from bot.db import SessionLocal, engine
from sqlalchemy import text

async def check_db():
    try:
        async with SessionLocal() as db:
            result = await db.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            
            # Check for tables
            result = await db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
            tables = [row[0] for row in result.fetchall()]
            print(f"Tables found: {', '.join(tables)}")
            
            # Check companies count (since user is working on API_TORTISH)
            from bot.models import Company
            from sqlalchemy import select, func
            result = await db.execute(select(func.count(Company.id)))
            count = result.scalar()
            print(f"Number of companies in DB: {count}")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_db())
