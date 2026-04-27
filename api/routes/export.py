from sqlalchemy import select, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from bot.models import KnowledgeBase, Message, User
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import io
import csv

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
        writer.writerow(["ID", "Foydalanuvchi", "Guruh ID", "Xabar matni", "Savolmi?", "Javob berilganmi?", "Javob matni", "Sana"])
        
        for item in data:
            ans_text = ""
            if item.is_answered:
                # Savolga tegishli javob xabarini qidiramiz
                ans_query = await db.execute(
                    select(Message).filter(
                        Message.group_id == item.group_id, 
                        Message.reply_to_message_id == item.telegram_message_id
                    ).limit(1)
                )
                answer = ans_query.scalars().first()
                if answer:
                    ans_text = answer.text
                elif not item.answered_by_bot:
                    # Agar admin panel orqali bo'lsa (history'da saqlangan bo'lishi mumkin)
                    ans_text = "Admin Panel orqali javob berilgan"

            writer.writerow([
                item.id, 
                item.full_name or item.username or "Noma'lum",
                item.group_id,
                item.text,
                "Ha" if item.is_question else "Yo'q",
                "Ha" if item.is_answered else "Yo'q",
                ans_text,
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


@router.get("/daily-report")
async def export_daily_report(date: str, db: AsyncSession = Depends(get_db)):
    try:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except:
            target_date = date

        # Savollarni olish
        qs_query = (
            select(Message)
            .filter(Message.is_question == True)
            .filter(cast(Message.created_at, Date) == target_date)
            .order_by(Message.id.asc())
        )
        qs_res = await db.execute(qs_query)
        questions = qs_res.scalars().all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Vaqti", "Kimdan", "Username", "Savol matni", "Holati", "Javob matni", "Javob berdi"])
        
        for q in questions:
            # Javobni topish
            ans_res = await db.execute(
                select(Message)
                .filter(Message.group_id == q.group_id)
                .filter(Message.reply_to_message_id == q.telegram_message_id)
                .limit(1)
            )
            answer = ans_res.scalars().first()
            
            status = "Javob berilgan" if q.is_answered else "Kutilmoqda"
            ans_text = answer.text if answer else (q.text if q.is_answered and not q.answered_by_bot else "")
            ans_by = answer.full_name if answer else ("Admin" if q.is_answered and not q.answered_by_bot else "")

            writer.writerow([
                q.created_at.strftime("%H:%M") if q.created_at else "",
                q.full_name or "Noma'lum",
                f"@{q.username}" if q.username else "anonim",
                q.text,
                status,
                ans_text,
                ans_by
            ])
            
        output.seek(0)
        filename = f"arxiv_{date}.csv"
        return StreamingResponse(
            iter([output.getvalue()]), 
            media_type="text/csv", 
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    finally:
        pass
