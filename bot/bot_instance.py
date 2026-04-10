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
    if _bot_instance is None:
        session = None
        if TELEGRAM_PROXY:
            session = AiohttpSession(proxy=TELEGRAM_PROXY)
        _bot_instance = Bot(token=TELEGRAM_TOKEN, session=session)
    return _bot_instance

async def close_bot_session(bot: Bot):
    """Closes the bot session if it exists."""
    if bot.session:
        await bot.session.close()
