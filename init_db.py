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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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
