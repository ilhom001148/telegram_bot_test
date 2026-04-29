import asyncio
import asyncpg

async def test():
    try:
        conn = await asyncpg.connect('postgresql://postgres:123@localhost:5433/telegram_ai')
        print("✅ SUCCESS: Database 'telegram_ai' connected on port 5433!")
        rows = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        print(f"Tables: {[r['table_name'] for r in rows]}")
        await conn.close()
    except Exception as e:
        print(f"❌ FAILED to connect: {e}")

if __name__ == "__main__":
    asyncio.run(test())
