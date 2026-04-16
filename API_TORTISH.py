import asyncio
import httpx
import json
from sqlalchemy.future import select
from bot.db import SessionLocal
from bot.models import Company

# ⬇️ TASHQI BAZAGA ULANISH PAROLLARI ⬇️
EXTERNAL_API_URL = "https://developer.uyqur.uz/dev/company/info-for-bot"
EXTERNAL_HEADERS = {
    "Authorization": "header 'X-Auth: KmuWyVtwBA2rPunnbwTVW5NYXl$eWlPSIsInZhbHVlI'", 
    "Content-Type": "application/json"
}

async def fetch_and_save():
    print("\n⏳ Tashqi serverga ulanish boshlandi...")
    try:
        async with httpx.AsyncClient() as client:
            # 1. So'rov yuborish
            response = await client.get(EXTERNAL_API_URL, headers=EXTERNAL_HEADERS, timeout=15.0)
            
            if response.status_code != 200:
                print(f"❌ Xatolik: Boshqa server so'rovni bekor qildi (Status: {response.status_code})")
                return
            
            data = response.json()
            
            companies_data = data.get("companies")
            data_data = data.get("data")
            
            print(f"DEBUG key 'companies': {type(companies_data)} -> {str(companies_data)[:100]}")
            print(f"DEBUG key 'data': {type(data_data)} -> {str(data_data)[:100]}")
            
            companies_list = []
            if isinstance(data, list):
                companies_list = data
            elif companies_data:
                companies_list = companies_data if isinstance(companies_data, list) else list(companies_data.values()) if isinstance(companies_data, dict) else []
            elif data_data:
                companies_list = data_data if isinstance(data_data, list) else list(data_data.values()) if isinstance(data_data, dict) else []
            
            if not companies_list:
                print("ℹ️ Server ulandi, lekin format boshqacha yoki kompaniyalar yo'q.")

                return
                
            print(f"✅ Ulandi! U yerdan jami {len(companies_list)} ta kompaniya tortib olindi. Yozish boshlanmoqda...\n")
            
            # 2. Bazaga ulanish va qo'shish
            async with SessionLocal() as db:
                added_count = 0
                for ext_company in companies_list:
                    # Malumotlarni aniqlash
                    name = str(ext_company.get("name") or ext_company.get("company_name") or "Noma'lum Kompaniya")
                    
                    # Tekshirish (Bazaga oldin yozilmagan bo'lishi kerak ism bo'yicha)
                    existing = await db.execute(select(Company).filter(Company.name == name))
                    if existing.scalars().first():
                        print(f"➖ Tashlab o'tildi (Bazangizda oldindan bor): {name}")
                        continue 
                        
                    # Tartiblash
                    phone = str(ext_company.get("phone") or ext_company.get("phone_number") or ext_company.get("contact") or "")
                    director = str(ext_company.get("director") or ext_company.get("owner") or "")
                    resp_name = str(ext_company.get("uyqur_support_username") or ext_company.get("responsible_name") or "")
                    resp_phone = str(ext_company.get("uyqur_support_phone") or ext_company.get("responsible_phone") or "")
                    
                    # Model yaratish
                    new_comp = Company(
                        name=name,
                        phone=phone if phone else None,
                        director=director if director else None,
                        responsible_name=resp_name if resp_name else None,
                        responsible_phone=resp_phone if resp_phone else None,
                        status="Yangi",
                        is_active=True
                    )
                    db.add(new_comp)
                    added_count += 1
                    print(f"➕ Yangi qo'shildi! : {name}")
                    
                await db.commit()
                print(f"\n🎉 BAJARILDI! Yangi {added_count} ta kompaniya doimiy xotirangizga yozib qo'yildi.")
                
    except Exception as e:
        print(f"\n❌ Kutilmagan qanaqadir xatolik yuz berdi: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_and_save())
