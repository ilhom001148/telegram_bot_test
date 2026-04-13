from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, cast, Date
from sqlalchemy.orm import joinedload
from api.dependencies import get_db
from bot.models import Message, Group
from fastapi import APIRouter, HTTPException, Depends


router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get("/")
async def get_messages(
    db: AsyncSession = Depends(get_db),
    search: str | None = None,
    is_question: bool | None = None,
    is_answered: bool | None = None,
    group_id: int | None = None,
    limit: int = 10,
    offset: int = 0,
):
    try:
        query = select(Message)

        if search:
            query = query.filter(Message.text.ilike(f"%{search}%"))

        if is_question is not None:
            query = query.filter(Message.is_question == is_question)

        if is_answered is not None:
            query = query.filter(Message.is_answered == is_answered)

        if group_id is not None:
            query = query.filter(Message.group_id == group_id)

        count_query = select(func.count()).select_from(query.alias())
        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0

        messages_res = await db.execute(
            query.order_by(Message.id.desc())
            .offset(offset)
            .limit(limit)
        )
        messages = messages_res.scalars().all()

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
                "ai_provider": message.ai_provider,
                "ai_model": message.ai_model,
                "prompt_tokens": message.prompt_tokens,
                "completion_tokens": message.completion_tokens,
                "total_tokens": message.total_tokens,
            })

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": result
        }

    finally:
        pass


@router.get("/{message_id}")
async def get_message_detail(message_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Message).filter(Message.id == message_id))
        message = result.scalars().first()

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
            "ai_provider": message.ai_provider,
            "ai_model": message.ai_model,
            "prompt_tokens": message.prompt_tokens,
            "completion_tokens": message.completion_tokens,
            "total_tokens": message.total_tokens,
        }

    finally:
        pass


@router.delete("/{message_id}")
async def delete_message(message_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Message).filter(Message.id == message_id))
        message = result.scalars().first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        await db.delete(message)
        await db.commit()
        return {"status": "success", "message": "Xabar o'chirildi"}
    finally:
        pass


@router.get("/archive/summary")
async def get_archive_summary(db: AsyncSession = Depends(get_db)):
    try:
        # Sanalar bo'yicha guruhlash va statistikani hisoblash
        # cast(Message.created_at, Date) sanani olish uchun ishlatiladi
        stats_query = (
            select(
                cast(Message.created_at, Date).label("date"),
                func.count(Message.id).label("total"),
                func.sum(cast(Message.is_answered, func.Integer)).label("answered")
            )
            .filter(Message.is_question == True)
            .group_by(cast(Message.created_at, Date))
            .order_by(cast(Message.created_at, Date).desc())
        )
        stats_res = await db.execute(stats_query)
        stats = stats_res.all()
        
        result = []
        for s in stats:
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
        pass


@router.get("/archive/questions-by-date/{date}")
async def get_questions_by_date(date: str, db: AsyncSession = Depends(get_db)):
    try:
        from datetime import datetime
        # String sanani date obyektiga o'tkazamiz (xato bo'lmasligi uchun)
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except:
            target_date = date

        # Savollarni olish
        qs_query = (
            select(Message)
            .options(joinedload(Message.group))
            .filter(Message.is_question == True)
            .filter(cast(Message.created_at, Date) == target_date)
            .order_by(Message.id.desc())
        )
        qs_res = await db.execute(qs_query)
        questions = qs_res.scalars().all()
        
        result = []
        for q in questions:
            # Ushbu savolga berilgan javobni qidirish
            ans_res = await db.execute(
                select(Message)
                .filter(Message.group_id == q.group_id)
                .filter(Message.reply_to_message_id == q.telegram_message_id)
                .limit(1)
            )
            answer = ans_res.scalars().first()
            
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
        pass