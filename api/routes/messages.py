from sqlalchemy import select, func, delete, cast, Date, Integer
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
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
    user_id: int | None = None,
    group_id: int | None = None,
    limit: int = 10,
    offset: int = 0,
):
    try:
        query = select(Message)

        if search:
            query = query.filter(Message.text.ilike(f"%{search}%"))

        if user_id is not None:
            query = query.filter(Message.user_id == user_id)

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
            query.options(joinedload(Message.group))
            .order_by(Message.id.desc())
            .offset(offset)
            .limit(limit)
        )
        messages = messages_res.scalars().all()

        # Savollarning javoblarini yig'ish (Optimallashgan)
        q_msg_ids = [m.telegram_message_id for m in messages if m.is_question]
        group_ids = list(set([m.group_id for m in messages if m.is_question]))
        ans_map = {}
        if q_msg_ids:
            ans_query = select(Message).filter(Message.group_id.in_(group_ids), Message.reply_to_message_id.in_(q_msg_ids))
            ans_res = await db.execute(ans_query)
            answers = ans_res.scalars().all()
            ans_map = {f"{a.group_id}_{a.reply_to_message_id}": a for a in answers}

        result = []
        for message in messages:
            answer = ans_map.get(f"{message.group_id}_{message.telegram_message_id}")
            result.append({
                "id": message.id,
                "telegram_message_id": message.telegram_message_id,
                "group_id": message.group_id,
                "user_id": message.user_id,
                "full_name": message.full_name,
                "username": message.username,
                "text": message.text,
                "is_question": message.is_question,
                "is_staff": message.is_staff,
                "is_answered": message.is_answered,
                "answered_by_bot": message.answered_by_bot,
                "reply_to_message_id": message.reply_to_message_id,
                "ai_provider": message.ai_provider,
                "ai_model": message.ai_model,
                "prompt_tokens": message.prompt_tokens,
                "completion_tokens": message.completion_tokens,
                "total_tokens": message.total_tokens,
                "created_at": message.created_at.isoformat() if message.created_at else None,
                "answered_at": message.answered_at.isoformat() if message.answered_at else None,
                "answer_text": answer.text if answer else (message.text if message.is_answered and not message.answered_by_bot else None)
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
            "is_staff": message.is_staff,
            "is_answered": message.is_answered,
            "answered_by_bot": message.answered_by_bot,
            "reply_to_message_id": message.reply_to_message_id,
            "ai_provider": message.ai_provider,
            "ai_model": message.ai_model,
            "prompt_tokens": message.prompt_tokens,
            "completion_tokens": message.completion_tokens,
            "total_tokens": message.total_tokens,
            "created_at": message.created_at.isoformat() if message.created_at else None,
            "answered_at": message.answered_at.isoformat() if message.answered_at else None,
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
        # [FIX] UTC dan Toshkent vaqtiga (+5 soat) o'girib, keyin guruhlaymiz
        from sqlalchemy import text
        tashkent_time = Message.created_at + text("INTERVAL '5 hours'")
        
        stats_query = (
            select(
                cast(tashkent_time, Date).label("date"),
                func.count(Message.id).label("total"),
                func.sum(cast(Message.is_answered, Integer)).label("answered")
            )
            .filter(Message.is_question == True)
            .group_by(cast(tashkent_time, Date))
            .order_by(cast(tashkent_time, Date).desc())
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
        from datetime import datetime, timedelta
        # String sanani date obyektiga o'tkazamiz (xato bo'lmasligi uchun)
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except:
            target_date = date

        from sqlalchemy import text
        tashkent_time = Message.created_at + text("INTERVAL '5 hours'")

        # Savollarni olish
        qs_query = (
            select(Message)
            .options(joinedload(Message.group))
            .filter(Message.is_question == True)
            .filter(cast(tashkent_time, Date) == target_date)
            .order_by(Message.id.asc())
        )
        qs_res = await db.execute(qs_query)
        questions = qs_res.scalars().all()

        if not questions:
            return []

        # Barcha savollarning telegram_message_id'larini yig'amiz
        q_msg_ids = [q.telegram_message_id for q in questions]
        group_ids = list(set([q.group_id for q in questions]))

        # Barcha javoblarni bir so'rovda olamiz (N+1 optimallashtirish)
        ans_query = (
            select(Message)
            .filter(Message.group_id.in_(group_ids))
            .filter(Message.reply_to_message_id.in_(q_msg_ids))
        )
        ans_res = await db.execute(ans_query)
        answers = ans_res.scalars().all()
        
        # Javoblarni map qilib olamiz (key: {group_id}_{reply_id})
        ans_map = {f"{a.group_id}_{a.reply_to_message_id}": a for a in answers}
        
        result = []
        for q in questions:
            answer = ans_map.get(f"{q.group_id}_{q.telegram_message_id}")
            
            result.append({
                "id": q.id,
                "telegram_link": q.telegram_link,
                "telegram_app_link": q.telegram_app_link,
                "text": q.text,
                "full_name": q.full_name,
                "is_answered": q.is_answered,
                "created_at": (q.created_at + timedelta(hours=5)).strftime("%H:%M"),
                "answered_at": (q.answered_at + timedelta(hours=5)).strftime("%H:%M") if q.answered_at else None,
                "username": q.username,
                "answer_text": answer.text if answer else (q.text if q.is_answered and not q.answered_by_bot else None),
                "answered_by": answer.full_name if answer else ("Admin" if q.is_answered and not q.answered_by_bot else None)
            })
        return result
    finally:
        pass