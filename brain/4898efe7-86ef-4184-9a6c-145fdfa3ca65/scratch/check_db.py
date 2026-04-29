import asyncio
from sqlalchemy import select, func, case
from bot.models import Message
from bot.db import SessionLocal
from datetime import datetime, timedelta

async def check():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        period = "1_week"
        start_date = now - timedelta(days=7)
        
        def df(q, col=Message.created_at):
            return q.filter(col >= start_date)
            
        print(f"Now (UTC): {now}")
        print(f"Start Date: {start_date}")
        
        # 1. total_tickets
        base_q = [Message.is_question == True, Message.is_staff == False]
        total_tickets = await db.scalar(df(select(func.count(Message.id)).filter(*base_q))) or 0
        print(f"Total Tickets: {total_tickets}")
        
        # 2. agent_performance
        q = df(select(Message.full_name, func.count(Message.id), func.avg(case((Message.answered_at != None, func.extract('epoch', Message.answered_at) - func.extract('epoch', Message.created_at)), else_=0))).filter(Message.is_staff == True).group_by(Message.full_name))
        res = await db.execute(q)
        rows = res.all()
        print(f"Agent Performance Rows: {len(rows)}")
        for name, count, avg_sec in rows:
            print(f"Name: {name}, Count: {count}, Avg Sec: {avg_sec}")

        # Check all staff messages without date filter
        all_staff = await db.execute(select(Message).filter(Message.is_staff == True))
        print(f"Total Staff Messages (No filter): {len(all_staff.all())}")
        
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(check())
