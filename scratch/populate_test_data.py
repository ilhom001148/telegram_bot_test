import asyncio
from datetime import datetime, timedelta, timezone
from bot.db import SessionLocal
from bot.models import Message, Group, Company, User
from sqlalchemy import select

async def populate_test_data():
    async with SessionLocal() as db:
        # 1. Create or get a test group
        group_title = "UyQur Bot Test Group"
        res = await db.execute(select(Group).filter(Group.title == group_title))
        group = res.scalars().first()
        if not group:
            group = Group(telegram_id=-1003907978784, title=group_title)
            db.add(group)
            await db.flush()

        # 2. Create a test company
        res = await db.execute(select(Company).filter(Company.name == "UyQur"))
        company = res.scalars().first()
        if not company:
            company = Company(name="UyQur", status="Active")
            db.add(company)
            await db.flush()

        now = datetime.now(timezone.utc)
        
        test_messages = [
            # Mahsulotlar tahlili uchun
            {"text": "Ombor qoldig'i noto'g'ri ko'rsatilyapti, iltimos tekshiring", "is_question": True, "is_staff": False, "offset": 120}, # 2 hours ago
            {"text": "CRM tizimida yangi mijoz qo'shishda xatolik beryapti", "is_question": True, "is_staff": False, "offset": 180},
            {"text": "Hisobotlarni Excel formatida yuklab olish funksiyasi kerak", "is_question": True, "is_staff": False, "offset": 240},
            {"text": "To'lov tizimi integratsiyasi qachon tayyor bo'ladi?", "is_question": True, "is_staff": False, "offset": 300},
            {"text": "Login qilishda parol esdan chiqqan bo'lsa nima qilish kerak?", "is_question": True, "is_staff": False, "offset": 360},
            
            # SLA va Agent stats uchun
            {"text": "Narxi qancha?", "is_question": True, "is_staff": False, "offset": 60, "answered": True, "ans_offset": 45}, # answered in 15 mins
            {"text": "Dastur qanday ishlaydi?", "is_question": True, "is_staff": False, "offset": 40, "answered": True, "ans_offset": 35}, # answered in 5 mins
            {"text": "Yordam kerak!", "is_question": True, "is_staff": False, "offset": 10, "answered": False}, # unanswered
        ]

        for m_data in test_messages:
            msg_time = now - timedelta(minutes=m_data["offset"])
            msg = Message(
                telegram_message_id=1000 + m_data["offset"],
                group_id=group.id,
                user_id=123456,
                full_name="Test User",
                text=m_data["text"],
                is_question=m_data["is_question"],
                is_staff=m_data["is_staff"],
                created_at=msg_time
            )
            
            if m_data.get("answered"):
                msg.is_answered = True
                msg.answered_at = now - timedelta(minutes=m_data["ans_offset"])
                msg.answered_by_bot = False
                # Add a reply message from staff
                reply = Message(
                    telegram_message_id=2000 + m_data["offset"],
                    group_id=group.id,
                    user_id=999999,
                    full_name="UyQur Support Agent",
                    text="Albatta, yordam beramiz!",
                    is_question=False,
                    is_staff=True,
                    created_at=now - timedelta(minutes=m_data["ans_offset"]),
                    reply_to_message_id=msg.telegram_message_id,
                    answered_at=now # Not really needed but good for consistency
                )
                db.add(reply)
            
            db.add(msg)

        await db.commit()
        print(f"✅ {len(test_messages)} ta test xabari qo'shildi.")

if __name__ == "__main__":
    asyncio.run(populate_test_data())
