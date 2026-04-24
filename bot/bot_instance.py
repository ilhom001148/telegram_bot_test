import asyncio
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from bot.config import TELEGRAM_TOKEN, TELEGRAM_PROXY

_bot_instance = None

def get_bot() -> Bot:
    """
    Returns a global Bot instance with proxy support if configured.
    """
    global _bot_instance
    
    # Agar bot obyekti bo'lsa-yu, lekin sessiyasi yopilgan bo'lsa, uni o'chirib yangidan yaratamiz
    if _bot_instance is not None:
        try:
            if _bot_instance.session and _bot_instance.session.closed:
                _bot_instance = None
                print("🔄 Bot sessiyasi yopiq ekan, yangisi yaratilmoqda...")
        except:
            _bot_instance = None

    if _bot_instance is None:
        session = None
        if TELEGRAM_PROXY:
            session = AiohttpSession(proxy=TELEGRAM_PROXY)
        
        token_preview = f"{TELEGRAM_TOKEN[:10]}...{TELEGRAM_TOKEN[-5:]}" if TELEGRAM_TOKEN else "MISSING"
        print(f"🤖 Bot yangidan yaratilmoqda. Token: {token_preview}")
        _bot_instance = Bot(token=TELEGRAM_TOKEN.strip(), session=session)
        
    return _bot_instance

async def close_bot_session(bot: Bot):
    """Closes the bot session if it exists."""
    if bot.session:
        await bot.session.close()
