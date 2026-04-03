from fastapi import APIRouter
from sqlalchemy import func

from bot.db import SessionLocal
from bot.models import Group, Message

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats():
    db = SessionLocal()

    try:
        total_groups = db.query(func.count(Group.id)).scalar() or 0

        total_messages = db.query(func.count(Message.id)).scalar() or 0

        total_questions = (
            db.query(func.count(Message.id))
            .filter(Message.is_question == True)
            .scalar()
            or 0
        )

        answered_questions = (
            db.query(func.count(Message.id))
            .filter(
                Message.is_question == True,
                Message.is_answered == True
            )
            .scalar()
            or 0
        )

        unanswered_questions = (
            db.query(func.count(Message.id))
            .filter(
                Message.is_question == True,
                Message.is_answered == False
            )
            .scalar()
            or 0
        )

        bot_answers = (
            db.query(func.count(Message.id))
            .filter(
                Message.answered_by_bot == True
            )
            .scalar()
            or 0
        )

        return {
            "total_groups": total_groups,
            "total_messages": total_messages,
            "total_questions": total_questions,
            "answered_questions": answered_questions,
            "unanswered_questions": unanswered_questions,
            "bot_answers": bot_answers,
        }

    finally:
        db.close()