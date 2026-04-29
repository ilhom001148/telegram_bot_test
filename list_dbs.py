import asyncio
import asyncpg

async def list_dbs():
    try:
        conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/postgres')
        rows = await conn.fetch('SELECT datname FROM pg_database WHERE datistemplate = false')
        print("MAVJUD BAZALAR RO'YXATI:")
        for r in rows:
            print(f"- {r['datname']}")
        await conn.close()
    except Exception as e:
        print(f"XATOLIK: {e}")

if __name__ == "__main__":
    asyncio.run(list_dbs())
