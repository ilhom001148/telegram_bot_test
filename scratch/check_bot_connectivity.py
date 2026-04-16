import asyncio
from bot.bot_instance import get_bot
from bot.config import TELEGRAM_TOKEN

async def check_bot():
    print(f"Token: {TELEGRAM_TOKEN[:10]}...")
    bot = get_bot()
    try:
        me = await bot.get_me()
        print(f"✅ Bot is online: @{me.username}")
    except Exception as e:
        print(f"❌ Bot error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(check_bot())
