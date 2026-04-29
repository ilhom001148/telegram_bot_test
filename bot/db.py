import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from dotenv import load_dotenv
load_dotenv()

# Render to'liq DATABASE_URL beradi, lokal uchun alohida qismlardan yig'amiz
DATABASE_URL_RAW = os.getenv("DATABASE_URL")

if not DATABASE_URL_RAW:
    from bot.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    
    # Majburiy host to'g'irlash (bug fix for 'localhoste')
    clean_host = DB_HOST.strip()
    if clean_host == "localhoste":
        clean_host = "localhost"
        
    DATABASE_URL = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{clean_host}:{DB_PORT}/{DB_NAME}"
    )
else:
    # Bo'sh joylarni olib tashlaymiz
    DATABASE_URL = DATABASE_URL_RAW.strip()
    
    # Neon uchun sslmode=require ni ssl=require ga almashtiramiz
    if "sslmode=require" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("sslmode=require", "ssl=require")
    
    # Prefixlarni to'g'irlaymiz
    prefixes = ["postgres://", "postgresql://", "postgresql+psycopg://"]
    for prefix in prefixes:
        if DATABASE_URL.startswith(prefix):
            DATABASE_URL = DATABASE_URL.replace(prefix, "postgresql+asyncpg://", 1)
            break

if not DATABASE_URL.startswith("postgresql+asyncpg://") and "://" in DATABASE_URL:
    DATABASE_URL = "postgresql+asyncpg://" + DATABASE_URL.split("://", 1)[1]

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()