import asyncio
import asyncpg
from datetime import datetime, timedelta

async def debug_data():
    try:
        conn = await asyncpg.connect('postgresql://postgres:123@localhost:5433/telegram_ai')
        print("✅ Connected to database!")
        
        # 1. Umumiy xabarlar soni
        count = await conn.fetchval("SELECT COUNT(*) FROM messages")
        print(f"Jami xabarlar (Total messages): {count}")
        
        # 2. Savollar soni
        q_count = await conn.fetchval("SELECT COUNT(*) FROM messages WHERE is_question = True")
        print(f"Jami savollar (Total questions): {q_count}")
        
        # 3. Oxirgi 7 kundagi savollar
        start_date = datetime.utcnow() - timedelta(days=7)
        q_7d = await conn.fetchval("SELECT COUNT(*) FROM messages WHERE is_question = True AND created_at >= $1", start_date)
        print(f"Oxirgi 7 kundagi savollar: {q_7d}")
        
        # 4. Vaqtni tekshirish
        last_m = await conn.fetchrow("SELECT created_at FROM messages ORDER BY created_at DESC LIMIT 1")
        if last_m:
            print(f"Eng oxirgi xabar vaqti: {last_m['created_at']}")
            print(f"Hozirgi UTC vaqt: {datetime.utcnow()}")
            
        await conn.close()
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(debug_data())
