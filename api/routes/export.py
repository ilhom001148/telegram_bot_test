import csv
import io
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from bot.db import SessionLocal
from bot.models import KnowledgeBase, Message, User

router = APIRouter(prefix="/export", tags=["Export"])

@router.get("/knowledge")
def export_knowledge():
    db = SessionLocal()
    try:
        data = db.query(KnowledgeBase).order_by(KnowledgeBase.id.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Savol (Qoida)", "Javob", "Sana"])
        
        for item in data:
            writer.writerow([
                item.id, 
                item.question, 
                item.answer, 
                item.created_at.strftime("%Y-%m-%d %H:%M") if item.created_at else ""
            ])
            
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]), 
            media_type="text/csv", 
            headers={"Content-Disposition": "attachment; filename=bilimlar_bazasi.csv"}
        )
    finally:
        db.close()


@router.get("/messages")
def export_messages():
    db = SessionLocal()
    try:
        data = db.query(Message).order_by(Message.id.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Foydalanuvchi", "Guruh ID", "Xabar matni", "Savolmi?", "Javob berilganmi?", "Sana"])
        
        for item in data:
            writer.writerow([
                item.id, 
                item.full_name or item.username or "Noma'lum",
                item.group_id,
                item.text,
                "Ha" if item.is_question else "Yo'q",
                "Ha" if item.is_answered else "Yo'q",
                item.created_at.strftime("%Y-%m-%d %H:%M") if item.created_at else ""
            ])
            
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]), 
            media_type="text/csv", 
            headers={"Content-Disposition": "attachment; filename=barcha_xabarlar.csv"}
        )
    finally:
        db.close()

@router.get("/users")
def export_users():
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.id.desc()).all()
        
        # Barcha xabarlarni sanash qismi users routeda bor edi. Biz oddiy export qilamiz qulayroq
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Telegram ID", "Ismi", "Username", "Ro'yxatdan o'tgan sana"])
        
        for item in users:
            writer.writerow([
                item.id,
                item.telegram_id,
                item.full_name or "",
                item.username or "",
                item.created_at.strftime("%Y-%m-%d %H:%M") if item.created_at else ""
            ])
            
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]), 
            media_type="text/csv", 
            headers={"Content-Disposition": "attachment; filename=mijozlar_royxati.csv"}
        )
    finally:
        db.close()
