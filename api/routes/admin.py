from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from api.dependencies import get_db, get_current_admin
from bot.crud import get_broadcast_targets
from bot.models import Group
from bot.bot_instance import get_bot, close_bot_session
from pydantic import BaseModel
import asyncio

router = APIRouter(prefix="/admin", tags=["Admin Tools"])

class BroadcastMessage(BaseModel):
    text: str
    target: str # "all", "groups", "users", "specific_group"
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

from datetime import datetime
from bot.models import ScheduledBroadcast

@router.post("/broadcast")
async def broadcast_message(
    data: BroadcastMessage,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    if data.scheduled_at:
        try:
            # Parse datetime
            scheduled_dt = datetime.fromisoformat(data.scheduled_at.replace("Z", "+00:00"))
            new_schedule = ScheduledBroadcast(
                text=data.text,
                target_group_id=data.group_id if data.target == "specific_group" else None,
                scheduled_at=scheduled_dt,
                status="pending"
            )
            db.add(new_schedule)
            db.commit()
            return {
                "status": "success",
                "message": f"Xabar rejalashtirildi: {scheduled_dt.strftime('%Y-%m-%d %H:%M')}"
            }
        except ValueError:
             return {"status": "error", "message": "Noto'g'ri sana formati."}

    # Zudlik bilan yuborish:
    targets = get_broadcast_targets(db)
    ids_to_send = []
    
    if data.target == "specific_group":
        if not data.group_id:
             return {"status": "error", "message": "Guruh tanlanmagan."}
        group = db.query(Group).filter(Group.id == data.group_id).first()
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
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    targets = get_broadcast_targets(db)
    return {
        "total_groups": len(targets["groups"]),
        "total_users": len(targets["users"])
    }

@router.get("/stats/extended")
async def get_extended_stats(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    # Bu yerda kelajakda chuqurroq statistika funksiyalarini yozish mumkin
    from bot.models import Message, Group
    total_messages = db.query(Message).count()
    total_questions = db.query(Message).filter(Message.is_question == True).count()
    total_groups = db.query(Group).count()
    total_users = db.query(Message.user_id).distinct().count()
    
    return {
        "total_messages": total_messages,
        "total_questions": total_questions,
        "total_groups": total_groups,
        "total_users": total_users
    }

@router.post("/clear-data")
async def clear_data(
    data: dict, # {"type": "messages" | "knowledge" | "all"}
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    from bot.models import Message, Group, KnowledgeBase, User
    
    data_type = data.get("type")
    
    if data_type == "messages":
        db.query(Message).delete()
        db.commit()
        return {"status": "success", "message": "Xabarlar tarixi tozalandi."}
    
    elif data_type == "knowledge":
        db.query(KnowledgeBase).delete()
        db.commit()
        return {"status": "success", "message": "Bilimlar bazasi tozalandi."}
    
    elif data_type == "all":
        # Hammasini tozalash (Adminlar va Sozlamalardan tashqari)
        db.query(Message).delete()
        db.query(Group).delete()
        db.query(User).delete()
        # Bilimlarni ham o'chiramizmi? Ha, 'all' deganda hammasi tushuniladi.
        db.query(KnowledgeBase).delete()
        db.commit()
        return {"status": "success", "message": "Barcha ma'lumotlar muvaffaqiyatli o'chirildi."}
    
    else:
        raise HTTPException(status_code=400, detail="Noto'g'ri tur (type) yuborildi.")
