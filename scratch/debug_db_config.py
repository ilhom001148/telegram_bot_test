import os
from dotenv import load_dotenv
load_dotenv()

from bot.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

print(f"DEBUG: DATABASE_URL (env): {os.getenv('DATABASE_URL')}")
print(f"DEBUG: DB_HOST: '{DB_HOST}'")
print(f"DEBUG: DB_PORT: '{DB_PORT}'")
print(f"DEBUG: DB_NAME: '{DB_NAME}'")
print(f"DEBUG: DB_USER: '{DB_USER}'")
print(f"DEBUG: DB_PASSWORD: '{DB_PASSWORD}'")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print(f"DEBUG: Constructed DATABASE_URL: {DATABASE_URL}")
