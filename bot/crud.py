from sqlalchemy.orm import Session
from sqlalchemy import or_
from bot.models import Group, Message, KnowledgeBase


def get_or_create_group(
    db: Session,
    telegram_id: int,
    title: str,
    username: str | None = None,
) -> Group:
    group = db.query(Group).filter(Group.telegram_id == telegram_id).first()

    if group:
        updated = False

        if group.title != title:
            group.title = title
            updated = True

        if group.username != username:
            group.username = username
            updated = True

        if updated:
            db.commit()
            db.refresh(group)

        return group

    group = Group(
        telegram_id=telegram_id,
        title=title,
        username=username,
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def create_message(
    db: Session,
    telegram_message_id: int,
    group_id: int,
    user_id: int | None,
    full_name: str | None,
    username: str | None,
    text: str | None,
    is_question: bool,
    reply_to_message_id: int | None = None,
) -> Message:
    msg = Message(
        telegram_message_id=telegram_message_id,
        group_id=group_id,
        user_id=user_id,
        full_name=full_name,
        username=username,
        text=text,
        is_question=is_question,
        reply_to_message_id=reply_to_message_id,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def find_question_by_telegram_message_id(
    db: Session,
    group_id: int,
    telegram_message_id: int,
) -> Message | None:
    return (
        db.query(Message)
        .filter(
            Message.group_id == group_id,
            Message.telegram_message_id == telegram_message_id,
            Message.is_question.is_(True),
        )
        .first()
    )


def mark_question_answered(
    db: Session,
    question: Message,
    answered_by_bot: bool = False,
) -> Message:
    question.is_answered = True
    question.answered_by_bot = answered_by_bot
    db.commit()
    db.refresh(question)
    return question


def get_all_knowledge(db: Session):
    return db.query(KnowledgeBase).all()


def search_knowledge(db: Session, query_text: str) -> KnowledgeBase | None:
    # A simple search via ILIKE (for more complex cases, full-text search or pgvector is recommended)
    search_term = f"%{query_text.lower()}%"
    return db.query(KnowledgeBase).filter(
        or_(
            KnowledgeBase.question.ilike(search_term),
            KnowledgeBase.answer.ilike(search_term)
        )
    ).first()


def create_knowledge(db: Session, question: str, answer: str) -> KnowledgeBase:
    kb = KnowledgeBase(question=question, answer=answer)
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb