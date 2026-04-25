import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot.db import SessionLocal
from bot.models import Message, Admin
from sqlalchemy import select
from bot.bot_instance import get_bot

async def test_reply():
    async with SessionLocal() as db:
        # Get the latest question
        result = await db.execute(
            select(Message)
            .filter(Message.is_question == True)
            .order_by(Message.id.desc())
            .limit(1)
        )
        question = result.scalars().first()
        
        if not question:
            print("❌ Savol topilmadi!")
            return

        print(f"❓ Savol topildi: ID={question.id}, Text='{question.text}'")
        
        # Get Chat ID
        chat_id = None
        if question.group_id:
            from bot.models import Group
            g_res = await db.execute(select(Group).filter(Group.id == question.group_id))
            group = g_res.scalars().first()
            if group:
                chat_id = group.telegram_id
        elif question.user_id:
            chat_id = question.user_id
            
        if not chat_id:
            print("❌ Chat ID topilmadi!")
            return
            
        print(f"🚀 Telegram orqali javob yuborish: ChatID={chat_id}")
        
        try:
            bot = get_bot()
            sent_msg = await bot.send_message(
                chat_id=chat_id,
                text=f"Test javob (Admin Paneldan simulyatsiya): {question.text[:10]}...",
                reply_to_message_id=question.telegram_message_id
            )
            print(f"✅ Xabar yuborildi! ID: {sent_msg.message_id}")
        except Exception as e:
            print(f"❌ Xatolik: {e}")

if __name__ == "__main__":
    asyncio.run(test_reply())
