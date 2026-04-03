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
            result.append({
                "id": group.id,
                "telegram_id": group.telegram_id,
                "title": group.title,
                "username": group.username,
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
            items.append({
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