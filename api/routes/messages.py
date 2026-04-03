from fastapi import APIRouter
from bot.db import SessionLocal
from bot.models import Message
from fastapi import HTTPException


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