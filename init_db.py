import bcrypt
from bot.models import Admin, Base
from bot.db import SessionLocal, engine

def get_password_hash(password):
    # bcrypt needs bytes
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def init_admin():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(Admin).filter(Admin.username == "admin").first()
        if not admin:
            hashed_pw = get_password_hash("12345")
            new_admin = Admin(username="admin", hashed_password=hashed_pw)
            db.add(new_admin)
            db.commit()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    init_admin()
