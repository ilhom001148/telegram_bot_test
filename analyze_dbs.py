import asyncio
import asyncpg

async def analyze_dbs():
    dbs_to_check = ['n75_db', 'n75', 'deportamend', 'postgres']
    for db_name in dbs_to_check:
        try:
            print(f"\n--- Checking database: {db_name} ---")
            conn = await asyncpg.connect(f'postgresql://postgres:123@localhost:5432/{db_name}')
            rows = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            tables = [r['table_name'] for r in rows]
            print(f"Tables found: {tables}")
            if 'messages' in tables or 'questions' in tables:
                print(f"🎯 FOUND! This database contains bot tables.")
            await conn.close()
        except Exception as e:
            print(f"Could not connect to {db_name}: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_dbs())
