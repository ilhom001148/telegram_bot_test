import requests
import json

API_URL = "http://127.0.0.1:8000" # Assuming local dev
TOKEN = "your_token_here" # I don't have the token, but I'll write a script that can be used or I'll just run a DB query

# Let's just run a DB query to see if there are any messages for the user
from bot.db import SessionLocal
from bot.models import Message, User
import asyncio

async def debug_messages():
    async with SessionLocal() as db:
        # Get all users to find one with questions
        res = await db.execute("SELECT telegram_id, full_name FROM users")
        users = res.all()
        print(f"Total users: {len(users)}")
        
        for tid, name in users:
            msg_res = await db.execute(f"SELECT COUNT(*) FROM messages WHERE user_id = {tid} AND is_question = true")
            count = msg_res.scalar()
            if count > 0:
                print(f"User {name} ({tid}) has {count} questions.")
                
                # Test query logic
                from sqlalchemy import select
                query = select(Message).filter(Message.user_id == tid).filter(Message.is_question == True)
                res = await db.execute(query)
                items = res.scalars().all()
                print(f"  Confirmed via select(): {len(items)} items found.")

if __name__ == "__main__":
    asyncio.run(debug_messages())
