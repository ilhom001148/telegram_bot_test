import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Superadminlar ro'yxati (Vergul bilan ajratilgan bo'lsa listga aylantiramiz)
_superadmins_str = os.getenv("SUPERADMINS", "")
SUPERADMINS = [int(id.strip()) for id in _superadmins_str.split(",") if id.strip().isdigit()]

# Admin Panel credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "123")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "telegram_ai")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Telegram API ulanish uchun Proxy
TELEGRAM_PROXY = os.getenv("TELEGRAM_PROXY", None)