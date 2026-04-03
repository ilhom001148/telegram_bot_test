from fastapi import APIRouter
from bot.db import SessionLocal
from bot.models import Message
from fastapi import HTTPException


router = APIRouter(prefix="/questions", tags=["Questions"])


def serialize_question(q):
    return {
        "id": q.id,
        "telegram_message_id": q.telegram_message_id,
        "group_id": q.group_id,
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
    limit: int = 10,
    offset: int = 0,
):
    db = SessionLocal()

    try:
        query = db.query(Message).filter(Message.is_question == True)

        total = query.count()

        questions = (
            query.order_by(Message.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [serialize_question(q) for q in questions]
        }

    finally:
        db.close()


@router.get("/unanswered")
def get_unanswered_questions(
    limit: int = 10,
    offset: int = 0,
):
    db = SessionLocal()

    try:
        query = db.query(Message).filter(
            Message.is_question == True,
            Message.is_answered == False
        )

        total = query.count()

        questions = (
            query.order_by(Message.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [serialize_question(q) for q in questions]
        }

    finally:
        db.close()


@router.get("/answered")
def get_answered_questions(
    limit: int = 10,
    offset: int = 0,
):
    db = SessionLocal()

    try:
        query = db.query(Message).filter(
            Message.is_question == True,
            Message.is_answered == True
        )

        total = query.count()

        questions = (
            query.order_by(Message.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [serialize_question(q) for q in questions]
        }

    finally:
        db.close()




@router.get("/{question_id}")
def get_question_detail(question_id: int):
    db = SessionLocal()

    try:
        question = db.query(Message).filter(
            Message.id == question_id,
            Message.is_question == True
        ).first()

        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        return {
            "id": question.id,
            "telegram_message_id": question.telegram_message_id,
            "group_id": question.group_id,
            "user_id": question.user_id,
            "full_name": question.full_name,
            "username": question.username,
            "text": question.text,
            "is_answered": question.is_answered,
            "answered_by_bot": question.answered_by_bot,
            "reply_to_message_id": question.reply_to_message_id,
        }

    finally:
        db.close()