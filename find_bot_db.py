import asyncio
import asyncpg

async def find_db():
    try:
        main_conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/postgres')
        dbs = await main_conn.fetch('SELECT datname FROM pg_database WHERE datistemplate = false')
        await main_conn.close()
        
        print(f"Scanning {len(dbs)} databases...")
        for db_row in dbs:
            db_name = db_row['datname']
            try:
                conn = await asyncpg.connect(f'postgresql://postgres:123@localhost:5432/{db_name}')
                rows = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
                tables = [r['table_name'] for r in rows]
                if 'messages' in tables:
                    print(f"✅ FOUND! Database: '{db_name}' contains 'messages' table.")
                await conn.close()
            except:
                pass
        print("Scan complete.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(find_db())
