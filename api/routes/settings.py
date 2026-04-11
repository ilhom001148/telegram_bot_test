from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from bot.db import SessionLocal
from bot.models import Setting
from api.dependencies import get_current_admin, get_db
from pydantic import BaseModel

router = APIRouter(prefix="/settings", tags=["Settings"])

class SettingUpdate(BaseModel):
    key: str
    value: str

@router.get("/")
async def get_settings(current_admin=Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Setting))
    settings = result.scalars().all()
    # Convert to a dictionary for easier consumption by frontend
    return {s.key: s.value for s in settings}

@router.put("/")
async def update_setting(data: SettingUpdate, current_admin=Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Setting).filter(Setting.key == data.key))
    setting = result.scalars().first()
    if setting:
        setting.value = data.value
    else:
        setting = Setting(key=data.key, value=data.value)
        db.add(setting)
    
    await db.commit()
    return {"status": "success", "key": data.key}

@router.delete("/clear-history")
async def clear_history(current_admin=Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    from bot.models import User, Group, Message, ScheduledBroadcast
    
    # Faqat muloqotga oid jadvallarni tozalash (KnowledgeBase va Setting saqlanib qoladi)
    await db.execute(delete(ScheduledBroadcast))
    await db.execute(delete(Message))
    await db.execute(delete(Group))
    await db.execute(delete(User))
    
    await db.commit()
    return {"status": "success", "message": "Muloqotlar tarixi tozalandi. AI bilimlari saqlab qolindi."}

@router.delete("/clear-everything") # Added separate route to fix duplicate code logic
async def clear_everything(current_admin=Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    from bot.models import User, Group, Message, KnowledgeBase, Setting, ScheduledBroadcast
    
    # Barcha jadvallarni tozalash (Butunlay format qilish)
    await db.execute(delete(ScheduledBroadcast))
    await db.execute(delete(Message))
    await db.execute(delete(Group))
    await db.execute(delete(User))
    await db.execute(delete(KnowledgeBase))
    await db.execute(delete(Setting))
    
    await db.commit()
    return {"status": "success", "message": "Butun tizim tozalandi."}
