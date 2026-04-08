from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.dependencies import get_db, get_current_admin
from bot.models import TelegramAdmin
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/tg-admins", tags=["Telegram Admins"])

class TelegramAdminCreate(BaseModel):
    telegram_id: int
    full_name: str | None = None
    username: str | None = None

@router.get("/")
def get_tg_admins(db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    admins = db.query(TelegramAdmin).order_by(TelegramAdmin.id.desc()).all()
    return admins

@router.post("/")
def add_tg_admin(data: TelegramAdminCreate, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    # Check if exists
    existing = db.query(TelegramAdmin).filter(TelegramAdmin.telegram_id == data.telegram_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ushbu ID allaqachon admin qilingan.")
    
    new_admin = TelegramAdmin(
        telegram_id=data.telegram_id,
        full_name=data.full_name,
        username=data.username
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

@router.delete("/{admin_id}")
def delete_tg_admin(admin_id: int, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    admin = db.query(TelegramAdmin).filter(TelegramAdmin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin topilmadi.")
    
    db.delete(admin)
    db.commit()
    return {"status": "success", "message": "Telegram admin o'chirildi."}
