import asyncio
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from bot.config import TELEGRAM_TOKEN, TELEGRAM_PROXY

def get_bot() -> Bot:
    """
    Returns a Bot instance with proxy support if configured.
    Note: This creates a new session each time if not carefully managed.
    For simple API calls, it's safer to use this way and close the session afterwards.
    """
    session = None
    if TELEGRAM_PROXY:
        session = AiohttpSession(proxy=TELEGRAM_PROXY)
    
    return Bot(token=TELEGRAM_TOKEN, session=session)

async def close_bot_session(bot: Bot):
    """Closes the bot session if it exists."""
    if bot.session:
        await bot.session.close()
