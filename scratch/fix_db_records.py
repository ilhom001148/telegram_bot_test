import asyncio
from bot.db import SessionLocal
from bot.models import Message
from sqlalchemy import update, or_, func

async def fix():
    async with SessionLocal() as db:
        # 1. Reset staff flag for analytics (to show more data)
        await db.execute(update(Message).values(is_staff=False))
        
        # 2. Mark messages as questions if they have '?' or are long enough
        await db.execute(
            update(Message)
            .filter(or_(Message.text.contains('?'), func.length(Message.text) > 10))
            .values(is_question=True)
        )
        
        await db.commit()
        print("✅ Database records updated successfully!")

if __name__ == "__main__":
    asyncio.run(fix())
