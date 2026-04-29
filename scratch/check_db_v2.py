
import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from bot.db import SessionLocal
from bot.models import Message, Question
from sqlalchemy import select, func

async def check_data():
    async with SessionLocal() as db:
        # Check Questions (Tickets)
        result = await db.execute(select(func.count()).select_from(Question))
        q_count = result.scalar()
        print(f"Total Questions/Tickets in DB: {q_count}")
        
        # Check last 5 questions
        result = await db.execute(select(Question).order_by(Question.id.desc()).limit(5))
        qs = result.scalars().all()
        for q in qs:
            print(f"Q ID: {q.id}, Text: {q.text[:30]}, Answered: {q.is_answered}, Answer: {q.answer_text[:20] if q.answer_text else 'None'}")

        # Check Messages
        result = await db.execute(select(func.count()).select_from(Message))
        m_count = result.scalar()
        print(f"Total Messages in DB: {m_count}")

if __name__ == "__main__":
    asyncio.run(check_data())
