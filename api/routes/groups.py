from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from api.dependencies import get_db
from bot.models import Group, Message

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("/")
async def get_groups(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Group).order_by(Group.id.desc()))
        groups = result.scalars().all()

        final_result = []
        for group in groups:
            total_msgs_res = await db.execute(select(func.count(Message.id)).filter(Message.group_id == group.id))
            total_messages = total_msgs_res.scalar() or 0
            
            total_qs_res = await db.execute(select(func.count(Message.id)).filter(Message.group_id == group.id, Message.is_question == True))
            total_questions = total_qs_res.scalar() or 0
            
            answered_qs_res = await db.execute(select(func.count(Message.id)).filter(Message.group_id == group.id, Message.is_question == True, Message.is_answered == True))
            answered_questions = answered_qs_res.scalar() or 0
            
            unanswered_questions = total_questions - answered_questions

            final_result.append({
                "id": group.id,
                "telegram_id": group.telegram_id,
                "title": group.title,
                "username": group.username,
                "total_messages": total_messages,
                "total_questions": total_questions,
                "answered_questions": answered_questions,
                "unanswered_questions": unanswered_questions,
            })

        return final_result
    finally:
        pass


@router.get("/{group_id}")
async def get_group_detail(group_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Group).filter(Group.id == group_id))
        group = result.scalars().first()

        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        count_res = await db.execute(select(func.count(Message.id)).filter(Message.group_id == group_id))
        message_count = count_res.scalar() or 0

        return {
            "id": group.id,
            "telegram_id": group.telegram_id,
            "title": group.title,
            "username": group.username,
            "messages_count": message_count,
        }
    finally:
        pass


@router.get("/{group_id}/messages")
async def get_group_messages(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    search: str | None = None,
    is_question: bool | None = None,
    is_answered: bool | None = None,
    limit: int = 10,
    offset: int = 0,
):
    try:
        g_result = await db.execute(select(Group).filter(Group.id == group_id))
        group = g_result.scalars().first()

        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        query = select(Message).filter(Message.group_id == group_id)

        if search:
            query = query.filter(Message.text.ilike(f"%{search}%"))

        if is_question is not None:
            query = query.filter(Message.is_question == is_question)

        if is_answered is not None:
            query = query.filter(Message.is_answered == is_answered)

        count_query = select(func.count()).select_from(query.alias())
        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0

        messages_res = await db.execute(
            query.order_by(Message.id.desc())
            .offset(offset)
            .limit(limit)
        )
        messages = messages_res.scalars().all()

        items = []
        for message in messages:
            # Ushbu xabarga berilgan javobni qidirish
            ans_res = await db.execute(
                select(Message)
                .filter(Message.group_id == message.group_id)
                .filter(Message.reply_to_message_id == message.telegram_message_id)
                .limit(1)
            )
            answer = ans_res.scalars().first()

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
        pass


@router.delete("/{group_id}")
async def delete_group(group_id: int, db: AsyncSession = Depends(get_db)):
    try:
        g_result = await db.execute(select(Group).filter(Group.id == group_id))
        group = g_result.scalars().first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Jumlatan shu guruhning barcha xabarlarini ham o'chiramiz
        await db.execute(delete(Message).filter(Message.group_id == group_id))
        await db.delete(group)
        await db.commit()
        return {"status": "success", "message": "Guruh va uning barcha xabarlari o'chirildi"}
    finally:
        pass