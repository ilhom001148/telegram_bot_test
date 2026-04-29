import asyncio
from bot.bot_instance import get_bot

async def check_webhook():
    bot = get_bot()
    try:
        info = await bot.get_webhook_info()
        print(f"Webhook URL: {info.url}")
        print(f"Has custom certificate: {info.has_custom_certificate}")
        print(f"Pending update count: {info.pending_update_count}")
        print(f"IP address: {info.ip_address}")
        print(f"Last error date: {info.last_error_date}")
        print(f"Last error message: {info.last_error_message}")
        print(f"Last synchronization error date: {info.last_synchronization_error_date}")
        print(f"Max connections: {info.max_connections}")
        print(f"Allowed updates: {info.allowed_updates}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(check_webhook())
