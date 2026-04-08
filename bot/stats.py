from aiogram import Router
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram.types import Message as TgMessage

from bot.db import SessionLocal
from bot.crud import get_group_stats, get_or_create_group
from bot.config import SUPERADMINS

router = Router()


from bot.models import TelegramAdmin

def is_superadmin(user_id: int) -> bool:
    # 1. .env dagi hardcoded adminlarni tekshirish
    if user_id in SUPERADMINS:
        return True
    
    # 2. Bazadan tekshirish
    db = SessionLocal()
    try:
        admin = db.query(TelegramAdmin).filter(TelegramAdmin.telegram_id == user_id).first()
        return admin is not None
    finally:
        db.close()


@router.message(Command("stats"))
async def group_stats(message: TgMessage):

    if not message.from_user or not is_superadmin(message.from_user.id):
        await message.answer("Bu bo‘lim faqat adminlar uchun.")
        return

    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.answer("Bu komanda faqat guruhda ishlaydi.")
        return

    db = SessionLocal()

    try:
        group = get_or_create_group(
            db=db,
            telegram_id=message.chat.id,
            title=message.chat.title or "Unknown Group",
            username=getattr(message.chat, "username", None),
        )

        stats = get_group_stats(db, group.id)

        text = (
            f"📊 Guruh statistikasi\n\n"
            f"Jami savollar: {stats['total_questions']}\n"
            f"Javob berilgan: {stats['answered_questions']}\n"
            f"Javobsiz qolgan: {stats['unanswered_questions']}"
        )

        await message.answer(text)

    finally:
        db.close()