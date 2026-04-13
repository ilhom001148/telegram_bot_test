import asyncio
from sqlalchemy import text
from bot.db import engine

async def migrate():
    async with engine.begin() as conn:
        print("🚀 Ma'lumotlar bazasi migratsiyasi boshlandi...")
        
        # 1. messages jadvaliga yangi AI ustunlarini qo'shish
        columns = [
            ("ai_provider", "VARCHAR(50)"),
            ("ai_model", "VARCHAR(100)"),
            ("prompt_tokens", "INTEGER DEFAULT 0"),
            ("completion_tokens", "INTEGER DEFAULT 0"),
            ("total_tokens", "INTEGER DEFAULT 0")
        ]
        
        for col_name, col_type in columns:
            try:
                # PostgreSQL uchun ALTER TABLE
                await conn.execute(text(f"ALTER TABLE messages ADD COLUMN {col_name} {col_type}"))
                print(f"✅ Ustun qo'shildi: {col_name}")
            except Exception as e:
                # Agar ustun allaqachon bo'lsa, xatoni o'tkazib yuboramiz
                if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                    print(f"ℹ️ Ustun allaqachon mavjud: {col_name}")
                else:
                    print(f"❌ Xatolik ({col_name}): {e}")

        # 2. user_id ni BigInteger ga o'tkazish (Telegram ID lar katta raqam bo'lgani uchun)
        try:
            await conn.execute(text("ALTER TABLE messages ALTER COLUMN user_id TYPE BIGINT"))
            print("✅ user_id turi BIGINT ga o'zgartirildi.")
        except Exception as e:
            print(f"ℹ️ user_id o'zgartirishda eslatma/xato: {e}")

        print("\n🎉 Migratsiya muvaffaqiyatli yakunlandi!")

if __name__ == "__main__":
    asyncio.run(migrate())
