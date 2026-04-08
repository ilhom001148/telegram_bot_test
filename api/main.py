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


@app.get("/")
def root():
    return {"message": "API is running"}