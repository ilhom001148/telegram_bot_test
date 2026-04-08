from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from bot.db import SessionLocal
from bot.models import Message, Group
from bot.crud import create_message, mark_question_answered
from bot.config import TELEGRAM_TOKEN
from api.dependencies import get_db, get_current_admin
from pydantic import BaseModel
from aiogram import Bot

router = APIRouter(prefix="/questions", tags=["Questions"])

class AnswerRequest(BaseModel):
    text: str

def serialize_question(q):
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
    }

@router.get("/")
def get_all_questions(
    limit: int = 15,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Message).options(joinedload(Message.group)).filter(Message.is_question == True)
    total = query.count()
    questions = query.order_by(Message.id.desc()).offset(offset).limit(limit).all()
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [serialize_question(q) for q in questions]
    }

@router.get("/unanswered")
def get_unanswered_questions(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Message).options(joinedload(Message.group)).filter(
        Message.is_question == True,
        Message.is_answered == False
    )
    total = query.count()
    questions = query.order_by(Message.id.desc()).offset(offset).limit(limit).all()
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
    db: Session = Depends(get_db)
):
    # 1. Savolni topish
    question = db.query(Message).options(joinedload(Message.group)).filter(
        Message.id == question_id,
        Message.is_question == True
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Savol topilmadi")
    
    # Guruh yoki shaxsiy chat ekanini aniqlash
    chat_id = question.group.telegram_id if question.group else question.user_id
    if not chat_id:
        raise HTTPException(status_code=400, detail="Savol yuborilgan chat/foydalanuvchi topilmadi")

    try:
        # 2. Telegram orqali javob yuborish
        from bot.bot_instance import get_bot, close_bot_session
        bot = get_bot()
        
        try:
            sent_msg = await bot.send_message(
                chat_id=chat_id,
                text=data.text,
                reply_to_message_id=question.telegram_message_id
            )
        finally:
            await close_bot_session(bot)

        # 3. Bazada javobni saqlash
        create_message(
            db=db,
            telegram_message_id=sent_msg.message_id,
            group_id=question.group_id,
            user_id=None,
            full_name="Admin (AI Panel)",
            username="admin",
            text=data.text,
            is_question=False,
            reply_to_message_id=question.telegram_message_id
        )

        # 4. Savolni 'answered' deb belgilash
        mark_question_answered(db, question, answered_by_bot=True)

        return {"status": "success", "message": "Javob muvaffaqiyatli yuborildi"}
    except Exception as e:
        print(f"Telegram Answer Error: {e}")
        raise HTTPException(status_code=500, detail=f"Telegramga javob yuborishda xatolik: {str(e)}")

@router.get("/{question_id}")
def get_question_detail(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Message).options(joinedload(Message.group)).filter(
        Message.id == question_id,
        Message.is_question == True
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Savol topilmadi")

    return serialize_question(question)