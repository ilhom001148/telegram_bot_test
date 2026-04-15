from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from bot.db import engine, Base, SessionLocal
from bot.models import Group, Message, KnowledgeBase, Admin, Setting, User, Company
from api.auth import hash_password
from api.routes.auth import router as auth_router
from api.routes.dashboard import router as dashboard_router
from api.routes.groups import router as groups_router
from api.routes.messages import router as messages_router
from api.routes.questions import router as questions_router
from api.routes.knowledge import router as knowledge_router
from api.routes.settings import router as settings_router
from api.routes.admin import router as admin_router
from api.routes.users import router as users_router
from api.routes.export import router as export_router
from api.routes.companies import router as companies_router

async def init_db():
    from sqlalchemy import text
    async with engine.begin() as conn:
        # 1. Jadvallarni yaratish (mavjud bo'lmasa)
        await conn.run_sync(Base.metadata.create_all)
        
        # 2. Mavjud jadvallarga yangi ustunlarni qo'shish (Migratsiya)
        columns = [
            ("ai_provider", "VARCHAR(50)"),
            ("ai_model", "VARCHAR(100)"),
            ("prompt_tokens", "INTEGER DEFAULT 0"),
            ("completion_tokens", "INTEGER DEFAULT 0"),
            ("total_tokens", "INTEGER DEFAULT 0"),
            ("is_staff", "BOOLEAN DEFAULT FALSE")
        ]
        
        for col_name, col_type in columns:
            try:
                await conn.execute(text(f"ALTER TABLE messages ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                print(f"✅ Tekshirildi/Qo'shildi (api/main): {col_name}")
            except Exception:
                pass
        
        # User jadvaliga is_staff qo'shish
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_staff BOOLEAN DEFAULT FALSE"))
        except Exception:
            pass
                
        try:
            await conn.execute(text("ALTER TABLE messages ALTER COLUMN user_id TYPE BIGINT"))
            print("✅ user_id turi BIGINT ga o'zgartirildi (api/main).")
        except Exception:
            pass

async def init_admin():
    async with SessionLocal() as db:
        try:
            from sqlalchemy import select, func
            result = await db.execute(select(func.count(Admin.id)))
            count = result.scalar()
            if count == 0:
                username = os.getenv("ADMIN_USERNAME", "admin")
                password = os.getenv("ADMIN_PASSWORD", "12345")
                db.add(Admin(username=username, hashed_password=hash_password(password)))
                await db.commit()
                print(f"Initial admin created: {username}")
        finally:
            await db.close()

app = FastAPI(title="Telegram Bot Admin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import asyncio
from bot.main import start_bot

@app.on_event("startup")
async def startup_event():
    await init_db()
    await init_admin()
    print("🚀 Starting Telegram Bot in the background...")
    asyncio.create_task(start_bot())


app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(groups_router)
app.include_router(messages_router)
app.include_router(questions_router)
app.include_router(knowledge_router)
app.include_router(settings_router)
app.include_router(admin_router)
app.include_router(users_router)
app.include_router(export_router)
app.include_router(companies_router)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os as _os

# Logo rasmlari uchun statik papka
logos_path = _os.path.join(_os.path.dirname(__file__), "..", "admin-panel", "public", "logos")
_os.makedirs(logos_path, exist_ok=True)
app.mount("/logos", StaticFiles(directory=logos_path), name="logos")

@app.get("/api-status")
def root():
    return {"message": "API is running"}

@app.post("/webhook/bot")
async def telegram_webhook(update: dict):
    """
    Telegram webhook endpoint + External Company Webhook Fallback.
    """
    # 1. Agar Telegramdan kelayotgan xabar bo'lsa
    if "update_id" in update:
        from bot.main import dp
        from bot.bot_instance import get_bot
        from aiogram.types import Update
        
        bot = get_bot()
        telegram_update = Update(**update)
        await dp.feed_update(bot, telegram_update)
        return {"ok": True}
        
    # 2. Agar BOSHQA TIZIMDAN (Tashqi bot) kelayotgan JSON Data bo'lsa
    from bot.db import SessionLocal
    from bot.models import Company
    
    async with SessionLocal() as db:
        try:
            # Tashqi bot qanday nom bilan yuborganini taxminan o'qiymiz
            name = update.get("name") or update.get("company_name") or update.get("title") or "Tashqi Tizim Kompaniyasi"
            phone = update.get("phone") or update.get("phone_number") or update.get("contact")
            director = update.get("director") or update.get("owner") or update.get("fullname")
            
            new_company = Company(
                name=str(name),
                phone=str(phone) if phone else None,
                director=str(director) if director else None,
                status="Yangi",
                is_active=True
            )
            
            db.add(new_company)
            await db.commit()
            print(f"✅ Tashqi Webhook orqali yangi kompaniya saqlandi: {name}")
            return {"status": "success", "message": "Ma'lumotlar 'Kompaniyalar' paneliga saqlandi"}
        except Exception as e:
            print("Webhook Company Save Error:", e)
            return {"status": "error", "message": str(e)}

@app.get("/bot-status")
async def bot_status():
    from bot.bot_instance import get_bot
    from bot.config import TELEGRAM_TOKEN
    
    if not TELEGRAM_TOKEN or "YOUR_TOKEN" in TELEGRAM_TOKEN:
        return {"status": "error", "message": "TELEGRAM_TOKEN not configured in environment variables"}
    
    try:
        bot = get_bot()
        me = await bot.get_me()
        await bot.session.close()
        return {
            "status": "online",
            "bot_username": me.username,
            "bot_id": me.id,
            "can_join_groups": me.can_join_groups,
            "can_read_all_group_messages": me.can_read_all_group_messages
        }
    except Exception as e:
        return {"status": "offline", "error": str(e)}

# Serve the pre-built React Admin Panel
base_dir = os.path.dirname(__file__)
dist_path = os.path.join(base_dir, "..", "admin-panel", "dist")

if os.path.isdir(os.path.join(dist_path, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")

@app.get("/{full_path:path}")
def serve_react_app(full_path: str):
    if not os.path.exists(os.path.join(dist_path, "index.html")):
        return {"detail": "Admin panel not built. API is running."}
    return FileResponse(os.path.join(dist_path, "index.html"))