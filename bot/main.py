import os
import time
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatType
from aiogram.types import Message as TgMessage, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ChatMemberUpdated
from aiogram.filters import CommandStart, Command
from aiogram.client.session.aiohttp import AiohttpSession
from sqlalchemy import select

from bot.config import TELEGRAM_TOKEN, TELEGRAM_PROXY, SUPERADMINS
from bot.db import SessionLocal
from bot.crud import (
    get_or_create_group,
    create_message,
    find_question_by_telegram_message_id,
    mark_question_answered,
    search_knowledge,
    get_setting,
    get_or_create_user,
    update_user_language,
    get_group_question_count
)
from bot.ai import detect_question, is_question_ai, get_ai_answer_async, transcribe_audio
from bot.strings import get_string
from bot.stats import router as stats_router
# Sinxronizatsiya endi kerak emas, live ko'rinishga o'tildi
# from bot.sync import fetch_and_sync_companies


# Bot va Dispatcher obyektlarini yaratish (session keyinroq qo'shiladi)
dp = Dispatcher()
dp.include_router(stats_router)


@dp.my_chat_member()
async def handle_my_chat_member(update: ChatMemberUpdated):
    """Bot guruhga qo'shilganda yoki uning huquqlari o'zgarganda ishlaydi."""
    if update.new_chat_member.status in ["member", "administrator"]:
        async with SessionLocal() as db:
            try:
                await get_or_create_group(
                    db=db,
                    telegram_id=update.chat.id,
                    title=update.chat.title or "Unknown Group",
                    username=getattr(update.chat, "username", None)
                )
                print(f"📡 Bot yangi guruhga qo'shildi: {update.chat.title}")
            finally:
                await db.close()


# Language selection keyboard removed as per user request

# [NEW] Admin Cache (Simple TTL cache for group admins)
# Structure: {(chat_id, user_id): (is_staff, timestamp)}
admin_cache = {}
ADMIN_CACHE_TTL = 86400 # 1 day (24 hours)

async def is_user_staff(chat_id: int, user_id: int) -> bool:
    """Checks if a user is an admin, creator, or superadmin."""
    # 1. Superadmin check
    if str(user_id) in SUPERADMINS:
        return True
    
    # 2. Cache check
    now = time.time()
    if (chat_id, user_id) in admin_cache:
        is_staff, ts = admin_cache[(chat_id, user_id)]
        if now - ts < ADMIN_CACHE_TTL:
            return is_staff

    # 3. Telegram API check
    try:
        from bot.bot_instance import get_bot
        bot = get_bot()
        member = await bot.get_chat_member(chat_id, user_id)
        is_staff = member.status in ["administrator", "creator"]
        admin_cache[(chat_id, user_id)] = (is_staff, now)
        return is_staff
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False


@dp.message(CommandStart())
async def handle_start(message: TgMessage):
    async with SessionLocal() as db:
        try:
            user = await get_or_create_user(
                db, 
                message.from_user.id, 
                message.from_user.full_name, 
                message.from_user.username
            )
            # Tilni har doim o'zbekcha qilib belgilaymiz
            if not user.language_code:
                await update_user_language(db, user.telegram_id, "uz")
                
            welcome_text = get_string("welcome", "uz")
            await message.answer(welcome_text)
        finally:
            await db.close()


# handle_lang_cmd and handle_lang_callback removed as per user request


async def process_text_message(message: TgMessage, text: str, db, user_lang: str):
    # Maintenance mode tekshirish
    is_maint = await get_setting(db, "maintenance_mode", "false") == "true"
    if is_maint:
        maint_text = await get_setting(db, "maintenance_text", get_string("maintenance", user_lang))
        await message.reply(f"🛠 {maint_text}")
        return

    if not text.strip():
        return
        
    # Savolligini tekshirish (Intellektual)
    if not await is_question_ai(text):
        return
        
    # [NEW] Tracking Mode (Faqat sanash rejimi)
    if await get_setting(db, "tracking_mode", "false") == "true":
        return
        
    # Avval bazadan qidiramiz
    kb_matches = await search_knowledge(db, text)
    context = None
    if kb_matches:
        context = "\n---\n".join([f"Ma'lumot {i+1}:\nSavol: {m.question}\nJavob: {m.answer}" for i, m in enumerate(kb_matches)])
    
    # [NEW] KB Only Mode check
    kb_only_mode = await get_setting(db, "kb_only_mode", "false")
    if kb_only_mode == "true" and not context:
        return # Ma'lumot topilmadi, jim turamiz

    ai_res = await get_ai_answer_async(text, context=context)
    ai_text = ai_res.get("text", "")
    usage = ai_res.get("usage")

    if ai_text.strip() == "IGNORE":
        await message.reply(get_string("only_it", user_lang))
        return

    # [NEW] AI topa olmagan bo'lsa (KB only rejimida)
    if ai_text.strip() == "NOT_FOUND":
        return

    if not ai_text:
        return

    sent_msg = await message.reply(ai_text)
    
    # Shaxsiy xabarlarda bot javobini saqlash o'chirildi


@dp.message(F.voice)
async def handle_voice(message: TgMessage):
    async with SessionLocal() as db:
        try:
            # 1. Ovozli xabarni yuklab olish
            file_id = message.voice.file_id
            file = await message.bot.get_file(file_id)
            file_path = f"voice_{file_id}.oga"
            await message.bot.download_file(file.file_path, file_path)
            
            # 2. Transkripsiya qilish (Matnga aylantirish)
            print(f"🎙 Processing voice from {message.from_user.id}...")
            text = await transcribe_audio(file_path)
            
            # 3. Vaqtinchalik faylni o'chirish
            if os.path.exists(file_path):
                os.remove(file_path)
                
            final_text = f"[Ovozli xabar]: {text}" if text else "[Ovozli xabar: Tahlil qilib bo'lmadi yoki bo'sh]"
                
            # 4. Bazaga saqlash
            # Guruh yoki shaxsiy chatligini aniqlaymiz
            is_group = message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]
            
            if is_group:
                group = await get_or_create_group(
                    db=db,
                    telegram_id=message.chat.id,
                    title=message.chat.title or "Unknown Group",
                    username=getattr(message.chat, "username", None),
                )
                group_id = group.id
            else:
                group = await get_or_create_group(db, message.chat.id, message.from_user.full_name)
                group_id = group.id
            
            # [NEW] Staff/Admin check
            is_staff = False
            if is_group and message.from_user:
                is_staff = await is_user_staff(message.chat.id, message.from_user.id)
    
            is_question = await is_question_ai(text) if text else False
            
            await create_message(
                db=db,
                telegram_message_id=message.message_id,
                group_id=group_id,
                user_id=message.from_user.id if message.from_user else None,
                full_name=message.from_user.full_name if message.from_user else None,
                username=message.from_user.username if message.from_user else None,
                text=final_text,
                is_question=is_question if not is_staff else False, # Count as question only if NOT staff
                is_staff=is_staff,
                reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None,
            )
            print(f"✅ Voice saved to DB: {message.from_user.id}")
            
            # AI ga yubormaymiz va javob bermaymiz - faqat baza uchun.
            
        except Exception as e:
            print("VOICE ERROR:", e)
        finally:
            await db.close()


@dp.message(F.chat.type == ChatType.PRIVATE)
async def handle_private_message(message: TgMessage):
    # Shaxsiy xabarlarga javob berish to'xtatildi
    return


async def respond_with_ai(message: TgMessage, text: str, user_lang: str, q_msg_db_id: int):
    """AI javobini fonda tayyorlaydi va yuboradi (Webhook timeout oldini olish uchun)."""
    async with SessionLocal() as db:
        try:
            # Re-fetch q_msg to ensure it's attached to the current session
            from bot.models import Message as DbMessage
            from bot.models import Group as DbGroup
            result = await db.execute(select(DbMessage).filter(DbMessage.id == q_msg_db_id))
            q_msg = result.scalars().first()
            if not q_msg:
                return

            # Group objectni ham olish
            result = await db.execute(select(DbGroup).filter(DbGroup.id == q_msg.group_id))
            group = result.scalars().first()

            # Knowledge base qidirish
            kb_matches = await search_knowledge(db, text)
            context = None
            if kb_matches:
                context = "\n---\n".join([f"Ma'lumot {i+1}:\nSavol: {m.question}\nJavob: {m.answer}" for i, m in enumerate(kb_matches)])
            
            # [NEW] KB Only Mode check
            kb_only_mode = await get_setting(db, "kb_only_mode", "false")
            if kb_only_mode == "true" and not context:
                return 

            ai_res = await get_ai_answer_async(text, context=context)
            ai_text = ai_res.get("text", "")
            usage = ai_res.get("usage")
            
            if ai_text.strip() == "NOT_FOUND" or not ai_text:
                return

            if ai_text.strip() == "IGNORE":
                if user_lang:
                    await message.reply(get_string("only_it", user_lang))
                return

            sent_msg = await message.reply(ai_text)

            # Bot javobini saqlash
            await create_message(
                db=db,
                telegram_message_id=sent_msg.message_id,
                group_id=q_msg.group_id,
                user_id=None,
                full_name="AI Bot",
                username=None,
                text=ai_text,
                is_question=False,
                reply_to_message_id=message.message_id,
                ai_provider=usage.get("provider") if usage else None,
                ai_model=usage.get("model") if usage else None,
                prompt_tokens=usage.get("prompt_tokens", 0) if usage else 0,
                completion_tokens=usage.get("completion_tokens", 0) if usage else 0,
                total_tokens=usage.get("total_tokens", 0) if usage else 0,
            )
            
            # Savolni bazada 'Javob berildi' deb belgilash
            await mark_question_answered(db=db, question=q_msg, answered_by_bot=True)
            print(f"✅ AI responded to message {message.message_id} in group {group.title if group else 'N/A'}")
        except Exception as e:
            print(f"❌ Background AI Error: {e}")
        finally:
            await db.close()


@dp.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def handle_group_message(message: TgMessage):
    # Tizim xabarlarini (foydalanuvchi qo'shilishi, chiqishi va h.k.) inobatga olmaymiz
    if any([message.new_chat_members, message.left_chat_member, message.new_chat_title, 
            message.new_chat_photo, message.delete_chat_photo, message.group_chat_created]):
        return

    async with SessionLocal() as db:
        try:
            group = await get_or_create_group(
                db=db,
                telegram_id=message.chat.id,
                title=message.chat.title or "Unknown Group",
                username=getattr(message.chat, "username", None),
            )

            text = message.text or message.caption or ""
            if not text.strip():
                return

            # Bot buyruqlarini (/stats, /start va h.k.) savol sifatida saqlashdan to'xtatish
            if text.strip().startswith("/"):
                return

            # [NEW] Staff/Admin check
            is_staff = await is_user_staff(message.chat.id, message.from_user.id) if message.from_user else False

            is_question = await is_question_ai(text)
            # Xabarni saqlash
            q_msg = await create_message(
                db=db,
                telegram_message_id=message.message_id,
                group_id=group.id,
                user_id=message.from_user.id if message.from_user else None,
                full_name=message.from_user.full_name if message.from_user else None,
                username=message.from_user.username if message.from_user else None,
                text=text,
                is_question=is_question if not is_staff else False, # Count as question only if NOT staff
                is_staff=is_staff,
                reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None,
            )

            # Savolga javob berilganligini tekshirish (Agar foydalanuvchi boshqa savolga reply qilib javob yozsa)
            if message.reply_to_message:
                replied_question = await find_question_by_telegram_message_id(
                    db=db, group_id=group.id, telegram_message_id=message.reply_to_message.message_id
                )
                if replied_question and not replied_question.is_answered:
                    await mark_question_answered(db=db, question=replied_question, answered_by_bot=message.from_user.is_bot)

            # AI JAVOB BERISH - BACKGROUND TASK
            if is_question and not is_staff:
                if await get_setting(db, "tracking_mode", "false") == "false":
                    user = await get_or_create_user(db, message.from_user.id, message.from_user.full_name, message.from_user.username)
                    # Fonda bajarish (Webhook darhol OK qaytarishi uchun)
                    asyncio.create_task(respond_with_ai(message, text, user.language_code, q_msg.id))
        except Exception as e:
            print("ERROR:", e)
        finally:
            await db.close()


@dp.channel_post()
async def handle_channel_post(message: TgMessage):
    """Kanal postlarini qabul qilish va admin panelga saqlash."""
    async with SessionLocal() as db:
        try:
            text = message.text or message.caption or ""
            if not text.strip():
                return

            # Kanal guruh sifatida saqlanadi
            group = await get_or_create_group(
                db=db,
                telegram_id=message.chat.id,
                title=message.chat.title or "Unknown Channel",
                username=getattr(message.chat, "username", None),
            )

            is_question = await is_question_ai(text)

            # Xabarni saqlash (kanalda from_user yo'q, shuning uchun kanal nomi ishlatiladi)
            q_msg = await create_message(
                db=db,
                telegram_message_id=message.message_id,
                group_id=group.id,
                user_id=None,
                full_name=message.chat.title or "Kanal",
                username=getattr(message.chat, "username", None),
                text=text,
                is_question=is_question,
                reply_to_message_id=None,
            )

            # Agar savol bo'lsa va tracking rejimi o'chiq bo'lsa, AI javob beradi
            if is_question:
                if await get_setting(db, "tracking_mode", "false") == "false":
                    asyncio.create_task(respond_with_ai(message, text, "uz", q_msg.id))

        except Exception as e:
            print("CHANNEL ERROR:", e)
        finally:
            await db.close()


async def broadcast_scheduler_worker():
    from bot.bot_instance import get_bot
    from bot.models import ScheduledBroadcast, Group
    from datetime import datetime, timezone
    from bot.db import SessionLocal
    from sqlalchemy import select
    while True:
        await asyncio.sleep(10)
        async with SessionLocal() as db:
            try:
                now_local = datetime.now()
                pending_query = await db.execute(
                    select(ScheduledBroadcast).filter(
                        ScheduledBroadcast.status == 'pending', 
                        ScheduledBroadcast.scheduled_at <= now_local
                    )
                )
                pending = pending_query.scalars().all()
                
                for p in pending:
                    p.status = 'processing'
                    await db.commit()
                    bot = get_bot()
                    if p.target_group_id:
                        group_query = await db.execute(select(Group).filter(Group.id == p.target_group_id))
                        group = group_query.scalars().first()
                        if group:
                            try:
                                await bot.send_message(group.telegram_id, p.text)
                                p.status = 'sent'
                            except:
                                p.status = 'failed'
                    else:
                        groups_query = await db.execute(select(Group))
                        groups = groups_query.scalars().all()
                        for grp in groups:
                            try:
                                await bot.send_message(grp.telegram_id, p.text)
                            except:
                                pass
                        p.status = 'sent'
                    await db.commit()
            except Exception as e:
                print("Scheduler Error:", e)
            finally:
                await db.close()


async def start_bot():

    from bot.bot_instance import get_bot
    from bot.config import TELEGRAM_TOKEN, WEBHOOK_URL, WEBHOOK_PASSIVE
    
    # Rejalashtirilgan ishlar orqa fonda parallel ishlaydi
    asyncio.create_task(broadcast_scheduler_worker())

    
    while True:
        try:
            if not TELEGRAM_TOKEN or "YOUR_TOKEN" in TELEGRAM_TOKEN:
                print("❌ CRITICAL ERROR: TELEGRAM_TOKEN topilmadi!")
                await asyncio.sleep(10)
                continue
                
            bot = get_bot()
            me = await bot.get_me()
            print(f"✅ Bot connected: @{me.username}")
            
            if WEBHOOK_PASSIVE:
                print("⚠️ Passive Webhook Mode enabled. Skipping webhook/polling management.")
                print("📡 Bot is waiting for updates via middleman webhook.")
                while True:
                    await asyncio.sleep(3600)
            elif WEBHOOK_URL:
                # ✅ O'z webhookimizni to'g'ridan-to'g'ri Telegramga ro'yxatdan o'tkazamiz
                webhook_endpoint = f"{WEBHOOK_URL.rstrip('/')}/webhook/bot"
                await bot.set_webhook(
                    url=webhook_endpoint,
                    drop_pending_updates=True,
                    allowed_updates=["message", "callback_query", "my_chat_member", "channel_post"]
                )
                print(f"✅ Webhook muvaffaqiyatli o'rnatildi: {webhook_endpoint}")
                print("📡 Telegram xabarlarni to'g'ridan-to'g'ri shu manzilga yuboradi.")
                # FastAPI server aktiv bo'lgani uchun bu yerda kutish kerak
                while True:
                    await asyncio.sleep(3600)
            else:
                print("⚠️ WEBHOOK_URL topilmadi. Polling rejimida boshlanmoqda...")
                # Lokal ishga tushirishda Webhook bilan konflikt bo'lmasligi uchun uni o'chiramiz
                await bot.delete_webhook(drop_pending_updates=True)
                await bot.session.close() # Close any lingering sessions before starting polling
                await dp.start_polling(bot, skip_updates=True)
                break
        except Exception as e:
            print(f"❌ Bot Error: {e}")
            await asyncio.sleep(10)
        finally:
            # Webhook rejimida session-ni yopmaslik kerak, chunki u FastAPI orqali ishlatiladi
            if not WEBHOOK_URL:
                try:
                    if 'bot' in locals() and bot.session:
                        await bot.session.close()
                except:
                    pass

if __name__ == "__main__":
    try:
        # Python 3.10+ uchun to'g'ri ishlash tartibi
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("Bot to'xtadi.")
