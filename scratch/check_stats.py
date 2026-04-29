import asyncio
import os
import sys

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.db import SessionLocal
from bot.models import Message
from sqlalchemy import select, func
from datetime import datetime, timedelta

async def check():
    async with SessionLocal() as db:
        now = datetime.utcnow()
        start_date = now - timedelta(days=7)
        
        # Jami
        q1 = select(func.count(Message.id))
        total = await db.scalar(q1)
        
        # Oxirgi 7 kundagi jami
        q2 = select(func.count(Message.id)).filter(Message.created_at >= start_date)
        total_7_days = await db.scalar(q2)
        
        # is_question == True and is_staff == False and last 7 days
        q3 = select(func.count(Message.id)).filter(
            Message.is_question == True, 
            Message.is_staff == False,
            Message.created_at >= start_date
        )
        tickets = await db.scalar(q3)
        
        print(f"Total messages in DB: {total}")
        print(f"Total in last 7 days: {total_7_days}")
        print(f"Tickets (is_question=True, is_staff=False, last 7 days): {tickets}")

if __name__ == "__main__":
    asyncio.run(check())
