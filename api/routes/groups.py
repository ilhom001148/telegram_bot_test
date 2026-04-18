from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from api.dependencies import get_db
from bot.models import Group, Message

router = APIRouter(prefix="/groups", tags=["Groups"])


# AI Pricing (USD per 1 Million tokens)
AI_PRICING = {
    "openai": {"prompt": 0.15, "completion": 0.60},
    "gemini": {"prompt": 0.075, "completion": 0.30},
    "groq": {"prompt": 0.59, "completion": 0.79},
}

async def calculate_ai_cost(db: AsyncSession, group_ids: list[int]):
    """Calculates total AI cost for a list of groups."""
    if not group_ids:
        return 0, 0.0
        
    # Har bir provayder bo'yicha tokenlarni yig'ish
    query = (
        select(
            Message.ai_provider,
            func.sum(Message.prompt_tokens).label("p_sum"),
            func.sum(Message.completion_tokens).label("c_sum"),
            func.sum(Message.total_tokens).label("t_sum")
        )
        .filter(Message.group_id.in_(group_ids))
        .group_by(Message.ai_provider)
    )
    result = await db.execute(query)
    rows = result.all()
    
    total_cost = 0.0
    total_tokens = 0
    
    for row in rows:
        provider = (row[0] or "openai").lower()
        p_tokens = row[1] or 0
        c_tokens = row[2] or 0
        t_tokens = row[3] or 0
        
        total_tokens += t_tokens
        
        # Narxni hisoblash
        pricing = AI_PRICING.get(provider, AI_PRICING["openai"])
        cost = (p_tokens * pricing["prompt"] / 1_000_000) + (c_tokens * pricing["completion"] / 1_000_000)
        total_cost += cost
        
    return total_tokens, round(total_cost, 6)

@router.get("/")
async def get_groups(db: AsyncSession = Depends(get_db)):
    try:
        # Barcha guruhlarni olamiz
        result = await db.execute(select(Group))
        all_groups = result.scalars().all()

        # Nomi bo'yicha guruhlash
        grouped_by_title = {}
        for g in all_groups:
            if g.title not in grouped_by_title:
                grouped_by_title[g.title] = []
            grouped_by_title[g.title].append(g)

        final_result = []
        for title, subgroups in grouped_by_title.items():
            ids = [g.id for g in subgroups]
            
            # Asosiy ma'lumotlar uchun eng oxirgi guruhni olamiz
            main_group = subgroups[-1]
            
            total_msgs_res = await db.execute(select(func.count(Message.id)).filter(Message.group_id.in_(ids)))
            total_messages = total_msgs_res.scalar() or 0
            
            total_qs_res = await db.execute(select(func.count(Message.id)).filter(Message.group_id.in_(ids), Message.is_question == True, Message.is_staff == False))
            total_questions = total_qs_res.scalar() or 0
            
            answered_qs_res = await db.execute(select(func.count(Message.id)).filter(Message.group_id.in_(ids), Message.is_question == True, Message.is_staff == False, Message.is_answered == True))
            answered_questions = answered_qs_res.scalar() or 0
            
            unanswered_questions = total_questions - answered_questions

            # AI Sarfini hisoblash
            tokens, cost = await calculate_ai_cost(db, ids)

            final_result.append({
                "id": main_group.id,
                "telegram_id": main_group.telegram_id,
                "title": title,
                "username": main_group.username,
                "total_messages": total_messages,
                "total_questions": total_questions,
                "answered_questions": answered_questions,
                "unanswered_questions": unanswered_questions,
                "total_tokens": tokens,
                "total_ai_cost": cost,
            })

        # ID bo'yicha teskari tartibda qaytaramiz
        final_result.sort(key=lambda x: x['id'], reverse=True)
        return final_result
    finally:
        pass


@router.get("/{group_id}")
async def get_group_detail(group_id: int, db: AsyncSession = Depends(get_db)):
    try:
        # Berilgan ID bo'yicha guruhni topamiz
        result = await db.execute(select(Group).filter(Group.id == group_id))
        target_group = result.scalars().first()

        if not target_group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Shu nomdagi barcha guruhlarni topamiz (bo'sh joylar va registrni inobatga olgan holda)
        g_result = await db.execute(select(Group.id).filter(func.trim(Group.title).ilike(func.trim(target_group.title))))
        all_ids = list(g_result.scalars().all())

        count_res = await db.execute(select(func.count(Message.id)).filter(Message.group_id.in_(all_ids)))
        message_count = count_res.scalar() or 0

        return {
            "id": target_group.id,
            "telegram_id": target_group.telegram_id,
            "title": target_group.title,
            "username": target_group.username,
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
        # Berilgan ID bo'yicha guruhni topamiz
        g_result = await db.execute(select(Group).filter(Group.id == group_id))
        target_group = g_result.scalars().first()

        if not target_group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Shu nomdagi barcha guruhlarni topamiz
        all_g_result = await db.execute(select(Group.id).filter(func.trim(Group.title).ilike(func.trim(target_group.title))))
        all_ids = list(all_g_result.scalars().all())

        query = select(Message).filter(Message.group_id.in_(all_ids))

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
            query.options(joinedload(Message.group))
            .order_by(Message.id.desc())
            .offset(offset)
            .limit(limit)
        )
        messages = messages_res.scalars().all()

        # Savollarning javoblarini yig'ish (Optimallashgan)
        q_msg_ids = [m.telegram_message_id for m in messages]
        group_ids = list(set([m.group_id for m in messages]))
        
        ans_map = {}
        if q_msg_ids:
            ans_query = select(Message).filter(Message.group_id.in_(group_ids), Message.reply_to_message_id.in_(q_msg_ids))
            ans_res = await db.execute(ans_query)
            answers = ans_res.scalars().all()
            ans_map = {f"{a.group_id}_{a.reply_to_message_id}": a for a in answers}

        items = []
        for message in messages:
            answer = ans_map.get(f"{message.group_id}_{message.telegram_message_id}")

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
                "is_staff": message.is_staff,
                "is_answered": message.is_answered,
                "answered_by_bot": message.answered_by_bot,
                "reply_to_message_id": message.reply_to_message_id,
                "created_at": message.created_at.isoformat() if message.created_at else None,
                "answer_text": answer.text if answer else None,
                "answered_by": answer.full_name if answer else None,
                "ai_provider": answer.ai_provider if answer else None,
                "ai_model": answer.ai_model if answer else None,
                "total_tokens": answer.total_tokens if answer else 0,
            })

        return {
            "group": {
                "id": target_group.id,
                "telegram_id": target_group.telegram_id,
                "title": target_group.title,
                "username": target_group.username,
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
        # Berilgan ID bo'yicha guruhni topamiz
        g_result = await db.execute(select(Group).filter(Group.id == group_id))
        target_group = g_result.scalars().first()
        if not target_group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Shu nomdagi barcha guruhlarni topamiz
        all_g_result = await db.execute(select(Group).filter(Group.title == target_group.title))
        subgroups = all_g_result.scalars().all()
        ids = [g.id for g in subgroups]

        # Barcha tegishli xabarlarni o'chiramiz
        await db.execute(delete(Message).filter(Message.group_id.in_(ids)))
        
        # Barcha tegishli guruhlarni o'chiramiz
        for sg in subgroups:
            await db.delete(sg)
            
        await db.commit()
        return {"status": "success", "message": f"'{target_group.title}' nomi ostidagi barcha guruhlar va ularning xabarlari o'chirildi"}
    finally:
        pass