from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select, func
from bot.models import Group, Message, KnowledgeBase, Setting, User

async def get_or_create_user(
    db: AsyncSession,
    telegram_id: int,
    full_name: str | None = None,
    username: str | None = None,
) -> User:
    result = await db.execute(select(User).filter(User.telegram_id == telegram_id))
    user = result.scalars().first()

    if user:
        updated = False
        if user.full_name != full_name:
            user.full_name = full_name
            updated = True
        if user.username != username:
            user.username = username
            updated = True
        if updated:
            await db.commit()
            await db.refresh(user)
        return user

    user = User(
        telegram_id=telegram_id,
        full_name=full_name,
        username=username,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_language(db: AsyncSession, telegram_id: int, lang_code: str) -> User | None:
    result = await db.execute(select(User).filter(User.telegram_id == telegram_id))
    user = result.scalars().first()
    if user:
        user.language_code = lang_code
        await db.commit()
        await db.refresh(user)
    return user


async def get_or_create_group(
    db: AsyncSession,
    telegram_id: int,
    title: str,
    username: str | None = None,
) -> Group:
    result = await db.execute(select(Group).filter(Group.telegram_id == telegram_id))
    group = result.scalars().first()

    if group:
        updated = False
        if group.title != title:
            group.title = title
            updated = True
        if group.username != username:
            group.username = username
            updated = True
        if updated:
            await db.commit()
            await db.refresh(group)
        return group

    group = Group(
        telegram_id=telegram_id,
        title=title,
        username=username,
    )
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


async def create_message(
    db: AsyncSession,
    telegram_message_id: int,
    group_id: int,
    user_id: int | None,
    full_name: str | None,
    username: str | None,
    text: str | None,
    is_question: bool,
    reply_to_message_id: int | None = None,
    ai_provider: str | None = None,
    ai_model: str | None = None,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0,
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
        ai_provider=ai_provider,
        ai_model=ai_model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


async def find_question_by_telegram_message_id(
    db: AsyncSession,
    group_id: int,
    telegram_message_id: int,
) -> Message | None:
    result = await db.execute(
        select(Message)
        .filter(
            Message.group_id == group_id,
            Message.telegram_message_id == telegram_message_id,
            Message.is_question.is_(True),
        )
    )
    return result.scalars().first()


async def mark_question_answered(
    db: AsyncSession,
    question: Message,
    answered_by_bot: bool = False,
) -> Message:
    question.is_answered = True
    question.answered_by_bot = answered_by_bot
    await db.commit()
    await db.refresh(question)
    return question


async def get_all_knowledge(db: AsyncSession):
    result = await db.execute(select(KnowledgeBase))
    return result.scalars().all()


async def search_knowledge(db: AsyncSession, query_text: str) -> KnowledgeBase | None:
    search_term = f"%{query_text.lower()}%"
    result = await db.execute(
        select(KnowledgeBase).filter(
            or_(
                KnowledgeBase.question.ilike(search_term),
                KnowledgeBase.answer.ilike(search_term)
            )
        )
    )
    return result.scalars().first()


async def create_knowledge(db: AsyncSession, question: str, answer: str) -> KnowledgeBase:
    kb = KnowledgeBase(question=question, answer=answer)
    db.add(kb)
    await db.commit()
    await db.refresh(kb)
    return kb


async def get_setting(db: AsyncSession, key: str, default: str = "") -> str:
    result = await db.execute(select(Setting).filter(Setting.key == key))
    setting = result.scalars().first()
    return setting.value if setting else default


async def get_broadcast_targets(db: AsyncSession):
    g_result = await db.execute(select(Group.telegram_id))
    group_ids = [g for g in g_result.scalars().all()]
    
    u_result = await db.execute(select(Message.user_id).filter(Message.user_id.isnot(None)).distinct())
    user_ids = [u for u in u_result.scalars().all()]
    
    return {
        "groups": group_ids,
        "users": list(set(user_ids))
    }


async def get_group_question_count(db: AsyncSession, group_id: int) -> int:
    result = await db.execute(
        select(func.count(Message.id)).filter(
            Message.group_id == group_id,
            Message.is_question.is_(True)
        )
    )
    return result.scalar()


async def get_group_stats(db: AsyncSession, group_id: int) -> dict:
    """Guruh statistikasini hisoblaydi: jami, javob berilgan va javobsiz savollar."""
    total_result = await db.execute(
        select(func.count(Message.id)).filter(
            Message.group_id == group_id,
            Message.is_question.is_(True)
        )
    )
    total_questions = total_result.scalar()

    answered_result = await db.execute(
        select(func.count(Message.id)).filter(
            Message.group_id == group_id,
            Message.is_question.is_(True),
            Message.is_answered.is_(True)
        )
    )
    answered_questions = answered_result.scalar()

    unanswered_questions = total_questions - answered_questions

    return {
        "total_questions": total_questions,
        "answered_questions": answered_questions,
        "unanswered_questions": unanswered_questions
    }


async def get_ai_usage_stats(db: AsyncSession, group_id: int | None = None) -> list:
    """AI provayderlari bo'yicha token sarfi statistikasini hisoblaydi."""
    query = select(
        Message.ai_provider,
        func.sum(Message.total_tokens).label("tokens"),
        func.count(Message.id).label("requests")
    ).filter(Message.ai_provider.isnot(None))

    if group_id:
        query = query.filter(Message.group_id == group_id)

    query = query.group_by(Message.ai_provider)
    result = await db.execute(query)
    return result.all()