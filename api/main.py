from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from bot.db import engine, Base, SessionLocal
from bot.models import Group, Message, KnowledgeBase, Admin, Setting, User, TelegramAdmin
from api.auth import hash_password
from api.routes.auth import router as auth_router
from api.routes.dashboard import router as dashboard_router
from api.routes.groups import router as groups_router
from api.routes.messages import router as messages_router
from api.routes.questions import router as questions_router
from api.routes.knowledge import router as knowledge_router
from api.routes.settings import router as settings_router
from api.routes.admin import router as admin_router
from api.routes.telegram_admins import router as tg_admins_router
from api.routes.users import router as users_router
from api.routes.export import router as export_router

# Jadvallarni yaratish va Initial Admin qo'shish
Base.metadata.create_all(bind=engine)

def init_admin():
    db = SessionLocal()
    try:
        if db.query(Admin).count() == 0:
            username = os.getenv("ADMIN_USERNAME", "admin")
            password = os.getenv("ADMIN_PASSWORD", "12345")
            db.add(Admin(username=username, hashed_password=hash_password(password)))
            db.commit()
            print(f"Initial admin created: {username}")
    finally:
        db.close()

init_admin()

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
app.include_router(tg_admins_router)
app.include_router(users_router)
app.include_router(export_router)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

@app.get("/api-status")
def root():
    return {"message": "API is running"}

@app.post("/webhook/bot")
async def telegram_webhook(update: dict):
    """
    Telegram webhook endpoint.
    """
    from bot.main import dp
    from bot.bot_instance import get_bot
    from aiogram.types import Update
    
    bot = get_bot()
    telegram_update = Update(**update)
    await dp.feed_update(bot, telegram_update)
    return {"ok": True}

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