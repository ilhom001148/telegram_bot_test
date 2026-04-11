from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from api.dependencies import get_db
from bot.models import User, Message

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
async def get_all_users(db: AsyncSession = Depends(get_db)):
    try:
        # User jadvalidagi barcha ma'lumotlarni oshamiz va habarlar stastikasini yuklaymiz
        u_result = await db.execute(select(User).order_by(User.created_at.desc()))
        users = u_result.scalars().all()
        
        # Osonroq so'rov qilish qatorlari:
        # Barcha xabarlarni user_id bilan sanash
        msg_counts_query = (
            select(Message.user_id, func.count(Message.id).label('total'))
            .filter(Message.user_id.isnot(None))
            .group_by(Message.user_id)
        )
        msg_counts_res = await db.execute(msg_counts_query)
        msg_counts = {str(row[0]): row[1] for row in msg_counts_res.all()}
        
        # Barcha so'rovlar(savollarni) user_id bilan sanash 
        q_counts_query = (
            select(Message.user_id, func.count(Message.id).label('questions'))
            .filter(Message.is_question == True)
            .filter(Message.user_id.isnot(None))
            .group_by(Message.user_id)
        )
        q_counts_res = await db.execute(q_counts_query)
        q_counts = {str(row[0]): row[1] for row in q_counts_res.all()}

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
        pass
