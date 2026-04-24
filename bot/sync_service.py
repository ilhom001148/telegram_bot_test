import asyncio
import httpx
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from bot.db import SessionLocal as AsyncSessionLocal
from bot.models import Company
from sqlalchemy import select

# TASHQI API MA'LUMOTLARI (Buni .env orqali boshqarish tavsiya etiladi)
EXTERNAL_API_URL = os.getenv("EXTERNAL_COMPANIES_API", "https://tashqi-baza-api.uz/v1/companies")
API_TOKEN = os.getenv("EXTERNAL_API_TOKEN", "")

async def sync_companies():
    """Tashqi bazadan kompaniyalarni olib kelish va yangilash funksiyasi"""
    print(f"[{datetime.now()}] 🔄 Tashqi baza bilan sinxronizatsiya boshlandi...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Tashqi API'ga murojaat
            headers = {}
            if API_TOKEN:
                headers["Authorization"] = f"Bearer {API_TOKEN}"
                
            response = await client.get(EXTERNAL_API_URL, headers=headers, timeout=60.0)
            
            if response.status_code != 200:
                print(f"❌ Xatolik: API javob bermadi ({response.status_code})")
                return

            external_data = response.json()
            # Agar ma'lumotlar list bo'lib kelsa
            if not isinstance(external_data, list):
                # Ba'zan ma'lumotlar 'data' yoki 'results' kaliti ostida keladi
                external_data = external_data.get('data', [])

            count_new = 0
            count_updated = 0

            async with AsyncSessionLocal() as session:
                for item in external_data:
                    name = item.get('name') or item.get('title')
                    if not name:
                        continue

                    # Bazada bor-yo'qligini tekshirish
                    stmt = select(Company).where(Company.name == name)
                    result = await session.execute(stmt)
                    company = result.scalar_one_or_none()

                    if not company:
                        # Yangi kompaniya qo'shish
                        new_company = Company(
                            name=name,
                            director=item.get('director', 'Nomalum'),
                            phone=item.get('phone', ''),
                            responsible_name=item.get('responsible', ''),
                            responsible_phone=item.get('responsible_phone', ''),
                            status="Yangi",
                            is_active=True
                        )
                        session.add(new_company)
                        count_new += 1
                    else:
                        # Ma'lumotlarni yangilash
                        company.director = item.get('director', company.director)
                        company.phone = item.get('phone', company.phone)
                        count_updated += 1

                await session.commit()
                print(f"✅ Sinxronizatsiya yakunlandi: {count_new} ta yangi, {count_updated} ta yangilandi.")
                
        except Exception as e:
            print(f"⚠️ Sinxronizatsiyada kutilmagan xatolik: {e}")

async def run_scheduler():
    """Har kuni soat 03:00 da ishga tushuvchi vazifa"""
    print("⏰ Avtomatik sinxronizatsiya scheduleri ishga tushdi (Har kuni soat 03:00 da)")
    while True:
        try:
            now = datetime.now()
            # Har kuni soat 03:00 da
            if now.hour == 3 and now.minute == 0:
                await sync_companies()
                await asyncio.sleep(70) # Bir daqiqadan ko'proq kutish
            
            await asyncio.sleep(40) # Har 40 soniyada vaqtni tekshirish
        except Exception as e:
            print(f"Schedulerda xatolik: {e}")
            await asyncio.sleep(60)
