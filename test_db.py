import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASS", "123")
    db_host = os.getenv("DB_HOST", "localhost").strip()
    if db_host == "localhoste": db_host = "localhost"
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "uyqur_db")
    
    url = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    print(f"Testing URL: {url}")
    
    try:
        engine = create_async_engine(url)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            print("✅ SUCCESS: Database connected successfully!")
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
