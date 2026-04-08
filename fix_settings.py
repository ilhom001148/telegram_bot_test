from bot.db import engine, SessionLocal, Base
from bot.models import Setting
import bot.models

# Create tables if not exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    # Initialize system_prompt if missing
    if not db.query(Setting).filter(Setting.key == "system_prompt").first():
        db.add(Setting(key="system_prompt", value="Sen jahondagi eng yuqori malakali, professional so'rovni savolligini aniqlab olib Umumiy savollarga javob beradigan botsan."))
        print("Initialized system_prompt")

    # Initialize company_info if missing  
    if not db.query(Setting).filter(Setting.key == "company_info").first():
        db.add(Setting(key="company_info", value="Bu bizning Telegram AI bot tizimimiz."))
        print("Initialized company_info")

    db.commit()
    print("Database settings fixed successfully!")
except Exception as e:
    print(f"Error initializing settings: {e}")
finally:
    db.close()
