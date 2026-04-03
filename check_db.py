from bot.db import SessionLocal
from bot.models import Message, Group

db = SessionLocal()

print("=== GROUPS ===")
groups = db.query(Group).all()
for g in groups:
    print(g.id, g.title, g.telegram_id)

print("\n=== MESSAGES ===")
messages = db.query(Message).order_by(Message.id.desc()).limit(10).all()

for m in messages:
    print(
        f"id={m.id} | msg_id={m.telegram_message_id} | "
        f"text={m.text} | is_question={m.is_question}"
    )

db.close()