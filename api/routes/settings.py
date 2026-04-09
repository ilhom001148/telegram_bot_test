from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from bot.db import SessionLocal
from bot.models import Setting
from api.dependencies import get_current_admin, get_db
from pydantic import BaseModel

router = APIRouter(prefix="/settings", tags=["Settings"])

class SettingUpdate(BaseModel):
    key: str
    value: str

@router.get("/")
def get_settings(current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    settings = db.query(Setting).all()
    # Convert to a dictionary for easier consumption by frontend
    return {s.key: s.value for s in settings}

@router.put("/")
def update_setting(data: SettingUpdate, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    setting = db.query(Setting).filter(Setting.key == data.key).first()
    if setting:
        setting.value = data.value
    else:
        setting = Setting(key=data.key, value=data.value)
        db.add(setting)
    
    db.commit()
    return {"status": "success", "key": data.key}

@router.delete("/clear-history")
def clear_history(current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    from bot.models import User, Group, Message, ScheduledBroadcast
    
    # Faqat muloqotga oid jadvallarni tozalash (KnowledgeBase va Setting saqlanib qoladi)
    db.query(ScheduledBroadcast).delete()  # Group'ga bog'langan bo'lishi mumkin!
    db.query(Message).delete()
    db.query(Group).delete()
    db.query(User).delete()
    
    db.commit()
    return {"status": "success", "message": "Muloqotlar tarixi tozalandi. AI bilimlari saqlab qolindi."}

@router.delete("/clear-all")
def clear_all(current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    from bot.models import User, Group, Message, KnowledgeBase, Setting, ScheduledBroadcast, TelegramAdmin
    
    # Barcha jadvallarni tozalash (Butunlay format qilish)
    db.query(ScheduledBroadcast).delete()
    db.query(Message).delete()
    db.query(Group).delete()
    db.query(User).delete()
    db.query(TelegramAdmin).delete()
    db.query(KnowledgeBase).delete()
    db.query(Setting).delete()
    
    db.commit()
    return {"status": "success", "message": "Butun tizim tozalandi."}
