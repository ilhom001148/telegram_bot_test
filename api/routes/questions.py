from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from bot.models import Message, Group
from bot.crud import create_message, mark_question_answered
from api.dependencies import get_db, get_current_admin
from pydantic import BaseModel

router = APIRouter(prefix="/questions", tags=["Questions"])

class AnswerRequest(BaseModel):
    text: str

def serialize_question(q, answer_msg=None):
    return {
        "id": q.id,
        "telegram_link": q.telegram_link,
        "telegram_app_link": q.telegram_app_link,
        "telegram_message_id": q.telegram_message_id,
        "group_id": q.group_id,
        "group_title": q.group.title if q.group else "Noma'lum",
        "user_id": q.user_id,
        "full_name": q.full_name,
        "username": q.username,
        "text": q.text,
        "is_answered": q.is_answered,
        "answered_by_bot": q.answered_by_bot,
        "reply_to_message_id": q.reply_to_message_id,
        "ai_provider": q.ai_provider,
        "ai_model": q.ai_model,
        "prompt_tokens": q.prompt_tokens,
        "completion_tokens": q.completion_tokens,
        "total_tokens": q.total_tokens,
        "is_staff": q.is_staff,
        "created_at": q.created_at.replace(tzinfo=timezone.utc).isoformat() if q.created_at else None,
        "answered_at": q.answered_at.replace(tzinfo=timezone.utc).isoformat() if q.answered_at else None,
        "answer_text": answer_msg.text if answer_msg else None,
        "answered_by": answer_msg.full_name if answer_msg else ("Bot" if q.answered_by_bot else None)
    }

@router.get("/")
async def get_all_questions(
    db: AsyncSession = Depends(get_db),
    limit: int = 15,
    offset: int = 0,
):
    query = select(Message).options(joinedload(Message.group)).filter(
        Message.is_question == True,
        Message.is_staff == False
    )
    
    count_query = select(func.count()).select_from(query.alias())
    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0
    
    questions_res = await db.execute(
        query.order_by(Message.id.desc())
        .offset(offset)
        .limit(limit)
    )
    questions = questions_res.scalars().all()
    
    # Har bir savol uchun javobni olish
    items = []
    for q in questions:
        answer_res = await db.execute(
            select(Message).filter(
                Message.reply_to_message_id == q.telegram_message_id,
                Message.group_id == q.group_id,
                Message.is_question == False
            ).order_by(Message.id.desc()).limit(1)
        )
        answer_msg = answer_res.scalars().first()
        items.append(serialize_question(q, answer_msg))
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items
    }

@router.get("/unanswered")
async def get_unanswered_questions(
    db: AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0,
):
    query = select(Message).options(joinedload(Message.group)).filter(
        Message.is_question == True,
        Message.is_answered == False,
        Message.is_staff == False
    )
    
    count_query = select(func.count()).select_from(query.alias())
    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0
    
    questions_res = await db.execute(
        query.order_by(Message.id.desc())
        .offset(offset)
        .limit(limit)
    )
    questions = questions_res.scalars().all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [serialize_question(q) for q in questions]
    }

@router.post("/{question_id}/answer")
async def answer_question(
    question_id: int,
    data: AnswerRequest,
    current_admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    # 1. Xabarni topish
    result = await db.execute(
        select(Message).options(joinedload(Message.group)).filter(
            Message.id == question_id
        )
    )
    question = result.scalars().first()

    if not question:
        raise HTTPException(status_code=404, detail="Xabar topilmadi")
    
    if question.is_staff:
        raise HTTPException(status_code=403, detail="Support xabarlariga bu yerdan javob berib bo'lmaydi")
    
    # Guruh yoki shaxsiy chat ekanini aniqlash
    chat_id = None
    if question.group and question.group.telegram_id:
        chat_id = int(question.group.telegram_id)
    elif question.user_id:
        chat_id = int(question.user_id)

    if not chat_id:
        print(f"❌ ERROR: Chat ID topilmadi! Question ID: {question_id}")
        raise HTTPException(status_code=400, detail="Xabar yuborilgan chat/foydalanuvchi topilmadi")

    try:
        # 2. Telegram orqali javob yuborish
        from bot.bot_instance import get_bot
        bot = get_bot()
        
        # Bot tokenini tekshirish (faqat log uchun)
        token_preview = f"{bot.token[:10]}...{bot.token[-5:]}"
        print(f"🚀 [API] Bot orqali yuborilmoqda. Token: {token_preview}, ChatID: {chat_id}")

        # Chatga kirish imkoniyatini tekshirish
        try:
            print(f"🔍 [API] Chat holatini tekshirish: {chat_id}...")
            chat_info = await bot.get_chat(chat_id)
            print(f"✅ [API] Chat topildi: {chat_info.title} ({chat_info.type})")
        except Exception as chat_err:
            print(f"❌ [API] Chatni topishda xato: {chat_err}")
            # Agar chat topilmasa, ID noto'g'ri yoki bot u yerda emas
            raise HTTPException(
                status_code=400, 
                detail=f"Bot bu guruhni ko'rmayapti (ChatID: {chat_id}). Bot guruhdan chiqarib yuborilgan yoki ID noto'g'ri. Iltimos, bot guruhda borligini tekshiring."
            )

        sent_msg = None
        try:
            # Avval reply qilib urinib ko'ramiz
            sent_msg = await bot.send_message(
                chat_id=chat_id,
                text=data.text,
                reply_to_message_id=question.telegram_message_id
            )
            print(f"✅ [API] Xabar yuborildi. ID: {sent_msg.message_id}")
        except Exception as e:
            # Agar reply message topilmasa (o'chib ketgan bo'lsa), oddiy xabar yuboramiz
            err_str = str(e).lower()
            if "not found" in err_str or "replied" in err_str or "reply" in err_str:
                print(f"⚠️ [API] Original xabar topilmadi yoki o'chirilgan ({e}), oddiy xabar sifatida yuborilmoqda...")
                user_mention = f"@{question.username}" if question.username else question.full_name or "Mijoz"
                sent_msg = await bot.send_message(
                    chat_id=chat_id,
                    text=f"{user_mention}, savolingizga javob (asl xabar o'chirilgan):\n\n{data.text}"
                )
                print(f"✅ [API] Oddiy xabar sifatida yuborildi. ID: {sent_msg.message_id}")
            else:
                # Boshqa turdagi xatolar (masalan: Bot blocked, Forbidden va h.k.)
                print(f"❌ [API] Telegram API xatosi: {e}")
                err_msg = str(e)
                if "forbidden" in err_msg.lower():
                    err_msg = "Bot guruhda xabar yuborish huquqiga ega emas yoki bot bloklangan."
                raise HTTPException(status_code=500, detail=f"Telegram API xatosi: {err_msg}")

        # 3. Bazada javobni saqlash
        await create_message(
            db=db,
            telegram_message_id=sent_msg.message_id,
            group_id=question.group_id,
            user_id=None,
            full_name="Admin (AI Panel)",
            username="admin",
            text=data.text,
            is_question=False,
            reply_to_message_id=question.telegram_message_id if sent_msg.reply_to_message else None
        )

        # 4. Savolni 'answered' deb belgilash
        await mark_question_answered(db, question, answered_by_bot=True)

        return {"status": "success", "message": "Javob muvaffaqiyatli yuborildi"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ SYSTEM ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Tizim xatosi: {str(e)}")

@router.get("/{question_id}")
async def get_question_detail(question_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Message).options(joinedload(Message.group)).filter(
            Message.id == question_id
        )
    )
    question = result.scalars().first()

    if not question:
        raise HTTPException(status_code=404, detail="Xabar topilmadi")

    return serialize_question(question)