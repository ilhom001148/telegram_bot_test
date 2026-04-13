import asyncio
import bcrypt
from sqlalchemy import select
from bot.models import Admin, Base
from bot.db import SessionLocal, engine
from bot.config import ADMIN_USERNAME, ADMIN_PASSWORD

def get_password_hash(password):
    # bcrypt needs bytes
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

async def init_db():
    from sqlalchemy import text
    async with engine.begin() as conn:
        # 1. Jadvallarni yaratish (mavjud bo'lmasa)
        await conn.run_sync(Base.metadata.create_all)
        
        # 2. Mavjud jadvallarga yangi ustunlarni qo'shish (Migratsiya)
        # messages jadvali uchun
        columns = [
            ("ai_provider", "VARCHAR(50)"),
            ("ai_model", "VARCHAR(100)"),
            ("prompt_tokens", "INTEGER DEFAULT 0"),
            ("completion_tokens", "INTEGER DEFAULT 0"),
            ("total_tokens", "INTEGER DEFAULT 0")
        ]
        
        for col_name, col_type in columns:
            try:
                await conn.execute(text(f"ALTER TABLE messages ADD COLUMN {col_name} {col_type}"))
                print(f"✅ Ustun qo'shildi (init_db): {col_name}")
            except Exception:
                # Ustun allaqachon bo'lsa xatoni o'tkazib yuboramiz
                pass
                
        try:
            await conn.execute(text("ALTER TABLE messages ALTER COLUMN user_id TYPE BIGINT"))
        except Exception:
            pass

async def init_admin():
    await init_db()
    async with SessionLocal() as db:
        try:
            # Mevjud admin bo'lsa uni .env dagi yangi ma'lumot bilan tekshirish/yangilash
            result = await db.execute(select(Admin).filter(Admin.username == ADMIN_USERNAME))
            admin = result.scalars().first()
            hashed_pw = get_password_hash(ADMIN_PASSWORD)
            
            if not admin:
                new_admin = Admin(username=ADMIN_USERNAME, hashed_password=hashed_pw)
                db.add(new_admin)
                await db.commit()
                print(f"Admin user '{ADMIN_USERNAME}' created from .env.")
            else:
                # Agar parol o'zgargan bo'lsa yangilash
                admin.hashed_password = hashed_pw
                await db.commit()
                print(f"Admin user '{ADMIN_USERNAME}' updated from .env.")
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(init_admin())
