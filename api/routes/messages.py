from sqlalchemy.orm import Session, joinedload
from bot.db import SessionLocal
from bot.models import Message, Group
from fastapi import APIRouter, HTTPException


router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get("/")
def get_messages(
    search: str | None = None,
    is_question: bool | None = None,
    is_answered: bool | None = None,
    group_id: int | None = None,
    limit: int = 10,
    offset: int = 0,
):
    db = SessionLocal()

    try:
        query = db.query(Message)

        if search:
            query = query.filter(Message.text.ilike(f"%{search}%"))

        if is_question is not None:
            query = query.filter(Message.is_question == is_question)

        if is_answered is not None:
            query = query.filter(Message.is_answered == is_answered)

        if group_id is not None:
            query = query.filter(Message.group_id == group_id)

        total = query.count()

        messages = (
            query.order_by(Message.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        result = []
        for message in messages:
            result.append({
                "id": message.id,
                "telegram_message_id": message.telegram_message_id,
                "group_id": message.group_id,
                "user_id": message.user_id,
                "full_name": message.full_name,
                "username": message.username,
                "text": message.text,
                "is_question": message.is_question,
                "is_answered": message.is_answered,
                "answered_by_bot": message.answered_by_bot,
                "reply_to_message_id": message.reply_to_message_id,
            })

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": result
        }

    finally:
        db.close()



@router.get("/{message_id}")
def get_message_detail(message_id: int):
    db = SessionLocal()

    try:
        message = db.query(Message).filter(Message.id == message_id).first()

        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        return {
            "id": message.id,
            "telegram_message_id": message.telegram_message_id,
            "group_id": message.group_id,
            "user_id": message.user_id,
            "full_name": message.full_name,
            "username": message.username,
            "text": message.text,
            "is_question": message.is_question,
            "is_answered": message.is_answered,
            "answered_by_bot": message.answered_by_bot,
            "reply_to_message_id": message.reply_to_message_id,
        }

    finally:
        db.close()

@router.delete("/{message_id}")
def delete_message(message_id: int):
    db = SessionLocal()
    try:
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        db.delete(message)
        db.commit()
        return {"status": "success", "message": "Xabar o'chirildi"}
    finally:
        db.close()

from sqlalchemy import func, cast, Date

@router.get("/archive/summary")
def get_archive_summary():
    db = SessionLocal()
    try:
        # Sanalar bo'yicha guruhlash va statistikani hisoblash
        # cast(Message.created_at, Date) sanani olish uchun ishlatiladi
        stats = (
            db.query(
                cast(Message.created_at, Date).label("date"),
                func.count(Message.id).label("total"),
                func.count(func.nullif(Message.is_answered, False)).label("answered"),
                func.count(func.nullif(Message.is_answered, True)).label("unanswered")
            )
            .filter(Message.is_question == True)
            .group_by(cast(Message.created_at, Date))
            .order_by(cast(Message.created_at, Date).desc())
            .all()
        )
        
        result = []
        for s in stats:
            # unanswered hisoblashi biroz xato bo'lishi mumkin nullif bilan, 
            # aniqroq variant: total - answered
            ans = s.answered or 0
            tot = s.total or 0
            result.append({
                "date": str(s.date),
                "total": tot,
                "answered": ans,
                "unanswered": tot - ans
            })
        return result
    finally:
        db.close()

@router.get("/archive/questions-by-date/{date}")
def get_questions_by_date(date: str):
    db = SessionLocal()
    try:
        from datetime import datetime
        # String sanani date obyektiga o'tkazamiz (xato bo'lmasligi uchun)
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except:
            target_date = date

        # Savollarni olish
        questions = (
            db.query(Message)
            .options(joinedload(Message.group))
            .filter(Message.is_question == True)
            .filter(cast(Message.created_at, Date) == target_date)
            .order_by(Message.id.desc())
            .all()
        )
        
        result = []
        for q in questions:
            # Ushbu savolga berilgan javobni qidirish
            # Agar bot yoki admin reply qilib javob bergan bo'lsa
            answer = (
                db.query(Message)
                .filter(Message.group_id == q.group_id)
                .filter(Message.reply_to_message_id == q.telegram_message_id)
                .first()
            )
            
            result.append({
                "id": q.id,
                "telegram_link": q.telegram_link,
                "telegram_app_link": q.telegram_app_link,
                "text": q.text,
                "full_name": q.full_name,
                "is_answered": q.is_answered,
                "created_at": q.created_at.strftime("%H:%M"),
                "username": q.username,
                "answer_text": answer.text if answer else None,
                "answered_by": answer.full_name if answer else None
            })
        return result
    finally:
        db.close()