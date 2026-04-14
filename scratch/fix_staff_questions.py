import asyncio
import os
import time
from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from bot.db import SessionLocal, engine
from bot.models import Message, User
from bot.config import SUPERADMINS
from bot.bot_instance import get_bot

async def fix_staff_messages():
    async with SessionLocal() as db:
        print("🔍 Scanning for staff messages...")
        
        # 1. Get all unique users from messages
        result = await db.execute(select(Message.user_id, Message.group_id).filter(Message.user_id.isnot(None)).distinct())
        user_groups = result.all()
        
        bot = get_bot()
        staff_count = 0
        fixed_messages = 0
        
        try:
            for user_id, telegram_group_id in user_groups:
                if not user_id or not telegram_group_id:
                    continue
                    
                is_staff = False
                
                # Check Superadmin
                if str(user_id) in SUPERADMINS:
                    is_staff = True
                else:
                    try:
                        # Check via Telegram API
                        # The telegram_group_id in DB might be the internal ID, we need the telegram_id
                        from bot.models import Group
                        g_res = await db.execute(select(Group).filter(Group.id == telegram_group_id))
                        group = g_res.scalars().first()
                        
                        if group and group.telegram_id:
                            member = await bot.get_chat_member(group.telegram_id, user_id)
                            is_staff = member.status in ["administrator", "creator"]
                    except Exception as e:
                        # Probably not in the group or error
                        pass
                
                if is_staff:
                    print(f"👤 Found staff user: {user_id}")
                    # Update all messages for this user in this group
                    upd = await db.execute(
                        update(Message)
                        .filter(Message.user_id == user_id, Message.group_id == telegram_group_id)
                        .values(is_staff=True, is_question=False)
                    )
                    fixed_messages += upd.rowcount
                    staff_count += 1
            
            await db.commit()
            print(f"✅ Finished! Found {staff_count} staff users. Fixed {fixed_messages} messages.")
            
        finally:
            from bot.bot_instance import close_bot_session
            await close_bot_session(bot)
            await db.close()

if __name__ == "__main__":
    asyncio.run(fix_staff_messages())
