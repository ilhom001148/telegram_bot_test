import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from dotenv import load_dotenv
load_dotenv()

# Render to'liq DATABASE_URL beradi, lokal uchun alohida qismlardan yig'amiz
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    from bot.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    DATABASE_URL = (
        f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
else:
    # Render postgres:// bersa, psycopg uchun postgresql+psycopg:// qilamiz
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()