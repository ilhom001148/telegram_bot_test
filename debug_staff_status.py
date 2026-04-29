import asyncio
import asyncpg
from datetime import datetime, timedelta

async def debug_staff_status():
    try:
        conn = await asyncpg.connect('postgresql://postgres:123@localhost:5433/telegram_ai')
        now = datetime.utcnow()
        start_date = now - timedelta(days=7)
        
        print(f"--- Data for last 7 days (since {start_date}) ---")
        rows = await conn.fetch("""
            SELECT is_staff, is_question, COUNT(*) 
            FROM messages 
            WHERE created_at >= $1 
            GROUP BY is_staff, is_question
        """, start_date)
        
        for r in rows:
            print(f"Is Staff: {r[0]}, Is Question: {r[1]}, Count: {r[2]}")
            
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_staff_status())
