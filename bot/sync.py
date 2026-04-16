import httpx
import asyncio
from sqlalchemy.future import select
from bot.db import SessionLocal
from bot.models import Company

EXTERNAL_API_URL = "https://developer.uyqur.uz/dev/company/info-for-bot"
EXTERNAL_HEADERS = {
    "X-Auth": "KmuWyVtwBA2rPunnbwTVW5NYXl$eWlPSIsInZhbHVlI",
    "Content-Type": "application/json"
}

async def fetch_and_sync_companies():
    """Tashqi API dan kompaniyalarni tortib oladi va bazaga saqlaydi."""
    print("\n⏳ Tashqi serverdan kompaniyalarni sinxronizatsiya qilish boshlandi...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(EXTERNAL_API_URL, headers=EXTERNAL_HEADERS, timeout=30.0)
            
            if response.status_code != 200:
                print(f"❌ Xatolik: Boshqa server so'rovni bekor qildi (Status: {response.status_code})")
                return {"status": "error", "message": f"Status: {response.status_code}"}
            
            data = response.json()
            companies_list = data if isinstance(data, list) else data.get("data", [])
            
            if not companies_list:
                print("ℹ️ Kompaniyalar topilmadi yoki format xato.")
                return {"status": "info", "message": "No companies found"}
                
            async with SessionLocal() as db:
                added_count = 0
                updated_count = 0
                
                for ext_company in companies_list:
                    # Malumotlarni aniqlash
                    name = str(ext_company.get("name") or ext_company.get("company_name") or "Noma'lum Kompaniya").strip()
                    
                    # Tekshirish (Bazada borligini tekshirish)
                    result = await db.execute(select(Company).filter(Company.name == name))
                    existing_comp = result.scalars().first()
                    
                    phone = str(ext_company.get("phone") or ext_company.get("phone_number") or ext_company.get("contact") or "")
                    director = str(ext_company.get("director") or ext_company.get("owner") or "")
                    resp_name = str(ext_company.get("uyqur_support_username") or ext_company.get("responsible_name") or "")
                    resp_phone = str(ext_company.get("uyqur_support_phone") or ext_company.get("responsible_phone") or "")

                    if existing_comp:
                        # Agar mavjud bo'lsa, ma'lumotlarini yangilashimiz ham mumkin (Ixtiyoriy)
                        # Hozircha faqat yo'qlarini qo'shamiz deb kelishdik, lekin yangilash yaxshi amaliyot
                        existing_comp.phone = phone if phone else existing_comp.phone
                        existing_comp.director = director if director else existing_comp.director
                        existing_comp.responsible_name = resp_name if resp_name else existing_comp.responsible_name
                        existing_comp.responsible_phone = resp_phone if resp_phone else existing_comp.responsible_phone
                        updated_count += 1
                        continue
                        
                    # Yangi model yaratish
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
                    
                await db.commit()
                msg = f"Sinxronizatsiya yakunlandi: {added_count} ta yangi qo'shildi, {updated_count} ta yangilandi."
                print(f"✅ {msg}")
                return {"status": "success", "added": added_count, "updated": updated_count, "message": msg}
                
    except Exception as e:
        error_msg = f"Kutilmagan xatolik: {e}"
        print(f"\n❌ {error_msg}")
        return {"status": "error", "message": error_msg}
