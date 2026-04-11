from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from api.dependencies import get_db, get_current_admin
from bot.crud import get_broadcast_targets
from bot.models import Group, Message, KnowledgeBase, User, ScheduledBroadcast
from bot.bot_instance import get_bot, close_bot_session
from pydantic import BaseModel
import asyncio
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Admin Tools"])

class BroadcastMessage(BaseModel):
    text: str
    target: str
    group_id: int | None = None
    scheduled_at: str | None = None # ISO format (Y-m-d H:M)

async def send_broadcast_task(target_ids: list, text: str):
    bot = get_bot()
    success_count = 0
    fail_count = 0
    print(f"\n🚀 Xabar yuborish boshlandi. Jami nishonlar: {len(target_ids)}")
    
    try:
        for tid in target_ids:
            try:
                await bot.send_message(chat_id=tid, text=text)
                success_count += 1
                print(f"✅ MUVAFFAQIYATLI: {tid} ga xabar ketdi.")
                await asyncio.sleep(0.05) # Bot bloklanmasligi uchun
            except Exception as e:
                fail_count += 1
                print(f"❌ XATO: {tid} ga yuborishda muammo: {str(e)}")
        
        print(f"\n📊 Broadcast tugadi. \n✅ Muvaffaqiyatli: {success_count} \n❌ Xatolik: {fail_count}\n")
    finally:
        await close_bot_session(bot)

@router.post("/broadcast")
async def broadcast_message(
    data: BroadcastMessage,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    if data.scheduled_at:
        try:
            # Parse datetime
            scheduled_dt = datetime.fromisoformat(data.scheduled_at.replace("Z", "+00:00")).replace(tzinfo=None)
            new_schedule = ScheduledBroadcast(
                text=data.text,
                target_group_id=data.group_id if data.target == "specific_group" else None,
                scheduled_at=scheduled_dt,
                status="pending"
            )
            db.add(new_schedule)
            await db.commit()
            return {
                "status": "success",
                "message": f"Xabar rejalashtirildi: {scheduled_dt.strftime('%Y-%m-%d %H:%M')}"
            }
        except ValueError:
             return {"status": "error", "message": "Noto'g'ri sana formati."}

    # Zudlik bilan yuborish:
    targets = await get_broadcast_targets(db)
    ids_to_send = []
    
    if data.target == "specific_group":
        if not data.group_id:
             return {"status": "error", "message": "Guruh tanlanmagan."}
        result = await db.execute(select(Group).filter(Group.id == data.group_id))
        group = result.scalars().first()
        if not group:
             return {"status": "error", "message": "Xato: Guruh bazadan topilmadi."}
        ids_to_send.append(group.telegram_id)
    else:
        if data.target in ["all", "groups"]:
            ids_to_send.extend(targets["groups"])
        if data.target in ["all", "users"]:
            ids_to_send.extend(targets["users"])
        ids_to_send = list(set(ids_to_send))
    
    if not ids_to_send:
        return {"status": "error", "message": "Yuborish uchun nishonlar topilmadi."}
    
    background_tasks.add_task(send_broadcast_task, ids_to_send, data.text)
    
    return {
        "status": "success", 
        "message": f"Xabar yuborish jarayoni boshlandi. Taxminiy nishonlar soni: {len(ids_to_send)}"
    }

@router.get("/broadcast/count")
async def get_broadcast_counts(
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    targets = await get_broadcast_targets(db)
    return {
        "total_groups": len(targets["groups"]),
        "total_users": len(targets["users"])
    }

@router.get("/stats/extended")
async def get_extended_stats(
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    msg_count_res = await db.execute(select(func.count(Message.id)))
    total_messages = msg_count_res.scalar() or 0
    
    qs_count_res = await db.execute(select(func.count(Message.id)).filter(Message.is_question == True))
    total_questions = qs_count_res.scalar() or 0
    
    grp_count_res = await db.execute(select(func.count(Group.id)))
    total_groups = grp_count_res.scalar() or 0
    
    usr_count_res = await db.execute(select(func.count(Message.user_id.distinct())))
    total_users = usr_count_res.scalar() or 0
    
    return {
        "total_messages": total_messages,
        "total_questions": total_questions,
        "total_groups": total_groups,
        "total_users": total_users
    }

@router.post("/clear-data")
async def clear_data(
    data: dict, # {"type": "messages" | "knowledge" | "all"}
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    data_type = data.get("type")
    
    if data_type == "messages":
        await db.execute(delete(Message))
        await db.commit()
        return {"status": "success", "message": "Xabarlar tarixi tozalandi."}
    
    elif data_type == "knowledge":
        await db.execute(delete(KnowledgeBase))
        await db.commit()
        return {"status": "success", "message": "Bilimlar bazasi tozalandi."}
    
    elif data_type == "all":
        # Hammasini tozalash (Adminlar va Sozlamalardan tashqari)
        await db.execute(delete(Message))
        await db.execute(delete(Group))
        await db.execute(delete(User))
        await db.execute(delete(KnowledgeBase))
        await db.commit()
        return {"status": "success", "message": "Barcha ma'lumotlar muvaffaqiyatli o'chirildi."}
    
    else:
        raise HTTPException(status_code=400, detail="Noto'g'ri tur (type) yuborildi.")
