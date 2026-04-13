import asyncio
from bot.db import SessionLocal
from bot.models import Setting
from sqlalchemy import select

async def update_settings():
    async with SessionLocal() as db:
        try:
            # 1. tracking_mode ni o'chiramiz (test uchun qulay)
            result = await db.execute(select(Setting).filter(Setting.key == "tracking_mode"))
            setting = result.scalars().first()
            if setting:
                setting.value = "false"
                print("✅ tracking_mode -> false")
            else:
                db.add(Setting(key="tracking_mode", value="false"))
                print("➕ tracking_mode qo'shildi -> false")
            
            # 2. stt_mode ni tekshiramiz (default local bo'lishi kerak, lekin biz forced-cloud qilmoqchi emasmiz, 
            # chunki ai.py da endi ffmpeg check bor)
            result = await db.execute(select(Setting).filter(Setting.key == "stt_mode"))
            stt_setting = result.scalars().first()
            if not stt_setting:
                db.add(Setting(key="stt_mode", value="local"))
                print("➕ stt_mode qo'shildi -> local")
            
            await db.commit()
            print("💾 Sozlamalar yangilandi.")
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(update_settings())
