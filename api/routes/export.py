import csv
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.dependencies import get_db
from bot.models import KnowledgeBase, Message, User

router = APIRouter(prefix="/export", tags=["Export"])

@router.get("/knowledge")
async def export_knowledge(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(KnowledgeBase).order_by(KnowledgeBase.id.desc()))
        data = result.scalars().all()
        
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
        pass


@router.get("/messages")
async def export_messages(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Message).order_by(Message.id.desc()))
        data = result.scalars().all()
        
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
        pass

@router.get("/users")
async def export_users(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).order_by(User.id.desc()))
        users = result.scalars().all()
        
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
        pass
