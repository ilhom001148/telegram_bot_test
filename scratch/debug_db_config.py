import os
from bot.config import DB_HOST, DB_PORT, DB_NAME, DB_USER
from bot.db import DATABASE_URL

print(f"DB_HOST from config: '{DB_HOST}'")
print(f"DATABASE_URL generated: '{DATABASE_URL}'")
