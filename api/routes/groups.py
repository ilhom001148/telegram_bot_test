from fastapi import APIRouter, HTTPException
from bot.db import SessionLocal
from bot.models import Group, Message

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("/")
def get_groups():
    db = SessionLocal()

    try:
        groups = db.query(Group).order_by(Group.id.desc()).all()

        result = []
        for group in groups:
            total_messages = db.query(Message).filter(Message.group_id == group.id).count()
            total_questions = db.query(Message).filter(Message.group_id == group.id, Message.is_question == True).count()
            answered_questions = db.query(Message).filter(Message.group_id == group.id, Message.is_question == True, Message.is_answered == True).count()
            unanswered_questions = total_questions - answered_questions

            result.append({
                "id": group.id,
                "telegram_id": group.telegram_id,
                "title": group.title,
                "username": group.username,
                "total_messages": total_messages,
                "total_questions": total_questions,
                "answered_questions": answered_questions,
                "unanswered_questions": unanswered_questions,
            })

        return result

    finally:
        db.close()


@router.get("/{group_id}")
def get_group_detail(group_id: int):
    db = SessionLocal()

    try:
        group = db.query(Group).filter(Group.id == group_id).first()

        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        message_count = db.query(Message).filter(
            Message.group_id == group_id
        ).count()

        return {
            "id": group.id,
            "telegram_id": group.telegram_id,
            "title": group.title,
            "username": group.username,
            "messages_count": message_count,
        }

    finally:
        db.close()


@router.get("/{group_id}/messages")
def get_group_messages(
    group_id: int,
    search: str | None = None,
    is_question: bool | None = None,
    is_answered: bool | None = None,
    limit: int = 10,
    offset: int = 0,
):
    db = SessionLocal()

    try:
        group = db.query(Group).filter(Group.id == group_id).first()

        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        query = db.query(Message).filter(Message.group_id == group_id)

        if search:
            query = query.filter(Message.text.ilike(f"%{search}%"))

        if is_question is not None:
            query = query.filter(Message.is_question == is_question)

        if is_answered is not None:
            query = query.filter(Message.is_answered == is_answered)

        total = query.count()

        messages = (
            query.order_by(Message.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        items = []
        for message in messages:
            # Ushbu xabarga berilgan javobni qidirish
            answer = (
                db.query(Message)
                .filter(Message.group_id == message.group_id)
                .filter(Message.reply_to_message_id == message.telegram_message_id)
                .first()
            )

            items.append({
                "id": message.id,
                "telegram_link": message.telegram_link,
                "telegram_app_link": message.telegram_app_link,
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
                "created_at": message.created_at.isoformat() if message.created_at else None,
                "answer_text": answer.text if answer else None,
                "answered_by": answer.full_name if answer else None,
            })

        return {
            "group": {
                "id": group.id,
                "telegram_id": group.telegram_id,
                "title": group.title,
                "username": group.username,
            },
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": items,
        }

    finally:
        db.close()

@router.delete("/{group_id}")
def delete_group(group_id: int):
    db = SessionLocal()
    try:
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Jumlatan shu guruhning barcha xabarlarini ham o'chiramiz
        db.query(Message).filter(Message.group_id == group_id).delete()
        db.delete(group)
        db.commit()
        return {"status": "success", "message": "Guruh va uning barcha xabarlari o'chirildi"}
    finally:
        db.close()