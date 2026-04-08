from fastapi import APIRouter
from bot.db import SessionLocal
from bot.models import User, Message
from sqlalchemy import func

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
def get_all_users():
    db = SessionLocal()
    try:
        # User jadvalidagi barcha ma'lumotlarni oshamiz va habarlar stastikasini yuklaymiz
        users = db.query(User).order_by(User.created_at.desc()).all()
        
        # Osonroq so'rov qilish qatorlari:
        # Barcha xabarlarni user_id bilan sanash
        msg_counts_raw = db.query(Message.user_id, func.count(Message.id).label('total')).filter(Message.user_id.isnot(None)).group_by(Message.user_id).all()
        msg_counts = {str(item[0]): item[1] for item in msg_counts_raw}
        
        # Barcha so'rovlar(savollarni) user_id bilan sanash 
        q_counts_raw = db.query(Message.user_id, func.count(Message.id).label('questions')).filter(Message.is_question == True).filter(Message.user_id.isnot(None)).group_by(Message.user_id).all()
        q_counts = {str(item[0]): item[1] for item in q_counts_raw}

        result = []
        for u in users:
            uid_str = str(u.telegram_id)
            total_msg = msg_counts.get(uid_str, 0)
            total_qs = q_counts.get(uid_str, 0)
            
            result.append({
                "id": u.id,
                "telegram_id": u.telegram_id,
                "full_name": u.full_name,
                "username": u.username,
                "language_code": u.language_code,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "total_messages": total_msg,
                "total_questions": total_qs
            })
            
        # Eng faol foydalanuvchilar yuqorida turishi uchun qayta tartiblash:
        result.sort(key=lambda x: x["total_messages"], reverse=True)
        return result
    finally:
        db.close()
