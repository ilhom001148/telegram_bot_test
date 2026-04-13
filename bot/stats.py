from aiogram import Router
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram.types import Message as TgMessage

from bot.db import SessionLocal
from bot.crud import get_group_stats, get_or_create_group, get_ai_usage_stats
from bot.config import SUPERADMINS

router = Router()


def is_superadmin(user_id: int) -> bool:
    # Faqat .env dagi hardcoded adminlarni tekshirish
    return user_id in SUPERADMINS


@router.message(Command("stats"))
async def group_stats(message: TgMessage):

    if not message.from_user or not is_superadmin(message.from_user.id):
        await message.answer("Bu bo‘lim faqat adminlar uchun.")
        return

    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.answer("Bu komanda faqat guruhda ishlaydi.")
        return

    async with SessionLocal() as db:
        try:
            group = await get_or_create_group(
                db=db,
                telegram_id=message.chat.id,
                title=message.chat.title or "Unknown Group",
                username=getattr(message.chat, "username", None),
            )

            stats = await get_group_stats(db, group.id)

            text = (
                f"📊 Guruh statistikasi\n\n"
                f"Jami savollar: {stats['total_questions']}\n"
                f"Javob berilgan: {stats['answered_questions']}\n"
                f"Javobsiz qolgan: {stats['unanswered_questions']}\n\n"
            )

            # AI Usage Stats qo'shish
            ai_stats = await get_ai_usage_stats(db, group.id)
            if ai_stats:
                text += "🤖 AI Provayderlar sarfi:\n"
                text += "-----------------------\n"
                for row in ai_stats:
                    provider = row[0].capitalize()
                    tokens = f"{row[1]:,}"
                    requests = row[2]
                    text += f"🔹 {provider}: {tokens} token ({requests} ta javob)\n"
            else:
                text += "🤖 AI sarfi haqida ma'lumot yo'q."

            await message.answer(text)

        except Exception as e:
            print(f"Stats Error: {e}")
        finally:
            await db.close()