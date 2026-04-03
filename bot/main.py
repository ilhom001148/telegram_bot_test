import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatType
from aiogram.types import Message as TgMessage
from aiogram.filters import CommandStart
from bot.config import TELEGRAM_TOKEN
from bot.db import SessionLocal
from bot.crud import (
    get_or_create_group,
    create_message,
    find_question_by_telegram_message_id,
    mark_question_answered,
    search_knowledge,
    create_knowledge
)
from bot.ai import detect_question, get_ai_answer

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def handle_start(message: TgMessage):
    await message.answer("Assalomu alaykum! Men faqat dasturlash va IT sohasiga oid savollarga javob beruvchi botman. Menga savolingizni yozishingiz, yoki guruhlarga qo'shib ishlatishingiz mumkin.")


@dp.message(F.chat.type == ChatType.PRIVATE)
async def handle_private_message(message: TgMessage):
    text = message.text or message.caption or ""
    if not text.strip():
        return
        
    # AI dan to'g'ridan-to'g'ri (knowledge base siz) yoki knowledge base qo'shsa ham bo'ladi
    ai_answer = get_ai_answer(text)
    if ai_answer.strip() == "IGNORE":
        await message.reply("Kechirasiz, men faqat dasturlash va IT sohasiga oid savollarga javob bera olaman.")
        return
    await message.reply(ai_answer)


@dp.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def handle_group_message(message: TgMessage):
    db = SessionLocal()

    try:
        group = get_or_create_group(
            db=db,
            telegram_id=message.chat.id,
            title=message.chat.title or "Unknown Group",
            username=getattr(message.chat, "username", None),
        )

        text = message.text or message.caption or ""

        if not text.strip():
            return

        is_question = detect_question(text)

        created = create_message(
            db=db,
            telegram_message_id=message.message_id,
            group_id=group.id,
            user_id=message.from_user.id if message.from_user else None,
            full_name=message.from_user.full_name if message.from_user else None,
            username=message.from_user.username if message.from_user else None,
            text=text,
            is_question=is_question,
            reply_to_message_id=message.reply_to_message.message_id
            if message.reply_to_message
            else None,
        )

        # Agar bu xabar boshqa savolga reply bo‘lsa, oldingi savolni answered qilamiz
        if message.reply_to_message:
            replied_question = find_question_by_telegram_message_id(
                db=db,
                group_id=group.id,
                telegram_message_id=message.reply_to_message.message_id,
            )

            if replied_question and not replied_question.is_answered:
                is_bot_reply = message.from_user.is_bot if message.from_user else False

                mark_question_answered(
                    db=db,
                    question=replied_question,
                    answered_by_bot=is_bot_reply,
                )

                print(
                    f"[ANSWERED] question_msg_id={replied_question.telegram_message_id} "
                    f"by_bot={is_bot_reply}"
                )

        print(
            f"[SAVED] group={group.title} msg_id={created.telegram_message_id} "
            f"is_question={created.is_question}"
        )

        # =========================
        # AI JAVOB BERISH QISMI
        # =========================
        if is_question:
            # 1. Avval knowledge base dan qidiramiz
            kb_match = search_knowledge(db, text)

            if kb_match:
                db_answer = kb_match.answer
                
                # Context bilan AI orqali ozgina "odamlarcha" ko'rinishda javob by format
                ai_answer = get_ai_answer(text, context=db_answer)
                
                if ai_answer.strip() == "IGNORE":
                    return

                sent_msg = await message.reply(ai_answer)

                # bot javobini ham messages table ga yozamiz
                create_message(
                    db=db,
                    telegram_message_id=sent_msg.message_id,
                    group_id=group.id,
                    user_id=None,
                    full_name="AI Bot",
                    username=None,
                    text=ai_answer,
                    is_question=False,
                    reply_to_message_id=message.message_id,
                )

                # savol answered bo‘ldi deb belgilaymiz
                mark_question_answered(
                    db=db,
                    question=created,
                    answered_by_bot=True,
                )

                print(f"[AI-DB-ANSWER] msg_id={message.message_id}")
                return

            # 2. Topilmasa AI dan olamiz (umumiy bilim)
            ai_answer = get_ai_answer(text)
            
            if ai_answer.strip() == "IGNORE":
                return

            # 3. Biz uni bazaga saqlamaymiz avtomat, faqat Admin orqali qo'shish kerak (shunda axlat yig'ilmaydi)
            # Lekin agar avtomat o'rganishni xohlasak saqlasa bo'ladi. Hozircha saqlamoqchi emasmiz yoki:
            create_knowledge(db, text, ai_answer)

            # 4. Groupga reply qilamiz
            sent_msg = await message.reply(ai_answer)

            # 5. Bot javobini ham messages table ga saqlaymiz
            create_message(
                db=db,
                telegram_message_id=sent_msg.message_id,
                group_id=group.id,
                user_id=None,
                full_name="AI Bot",
                username=None,
                text=ai_answer,
                is_question=False,
                reply_to_message_id=message.message_id,
            )

            # 6. Savol answered deb belgilanadi
            mark_question_answered(
                db=db,
                question=created,
                answered_by_bot=True,
            )

            print(f"[AI-NEW-ANSWER] msg_id={message.message_id}")

    except Exception as e:
        print("ERROR:", e)

    finally:
        db.close()


async def main():
    print("Bot started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())