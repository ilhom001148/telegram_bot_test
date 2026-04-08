import bcrypt
from bot.models import Admin, Base
from bot.db import SessionLocal, engine

def get_password_hash(password):
    # bcrypt needs bytes
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

from bot.config import ADMIN_USERNAME, ADMIN_PASSWORD

def init_admin():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Mevjud admin bo'lsa uni .env dagi yangi ma'lumot bilan tekshirish/yangilash
        admin = db.query(Admin).filter(Admin.username == ADMIN_USERNAME).first()
        hashed_pw = get_password_hash(ADMIN_PASSWORD)
        
        if not admin:
            new_admin = Admin(username=ADMIN_USERNAME, hashed_password=hashed_pw)
            db.add(new_admin)
            db.commit()
            print(f"Admin user '{ADMIN_USERNAME}' created from .env.")
        else:
            # Agar parol o'zgargan bo'lsa yangilash
            admin.hashed_password = hashed_pw
            db.commit()
            print(f"Admin user '{ADMIN_USERNAME}' updated from .env.")
    finally:
        db.close()

if __name__ == "__main__":
    init_admin()
