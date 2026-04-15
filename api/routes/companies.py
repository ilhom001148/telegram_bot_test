import os
import re
import uuid
import shutil
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.dependencies import get_db
from bot.models import Company
from typing import Optional

router = APIRouter(prefix="/companies", tags=["Companies"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "admin-panel", "public", "logos")
os.makedirs(UPLOAD_DIR, exist_ok=True)

PHONE_RE = re.compile(r"^\+?[\d\s\-\(\)]{7,20}$")
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/svg+xml"}
MAX_LOGO_SIZE = 5 * 1024 * 1024  # 5 MB


def validate_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None
    phone = phone.strip()
    if phone and not PHONE_RE.match(phone):
        raise HTTPException(status_code=422, detail=f"Telefon raqami noto'g'ri formatda: '{phone}'. Misol: +998901234567")
    return phone


def serialize_company(c: Company) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "logo_url": c.logo_url,
        "brand_name": c.brand_name,
        "main_currency": c.main_currency,
        "extra_currency": c.extra_currency,
        "phone": c.phone,
        "director": c.director,
        "responsible_name": c.responsible_name,
        "responsible_phone": c.responsible_phone,
        "status": c.status,
        "subscription_start": c.subscription_start.isoformat() if c.subscription_start else None,
        "subscription_end": c.subscription_end.isoformat() if c.subscription_end else None,
        "is_active": c.is_active,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


# ─── GET all ──────────────────────────────────────────────────────────────────
@router.get("/")
async def get_companies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).order_by(Company.id.desc()))
    companies = result.scalars().all()
    return [serialize_company(c) for c in companies]


# ─── GET one ──────────────────────────────────────────────────────────────────
@router.get("/{company_id}")
async def get_company(company_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).filter(Company.id == company_id))
    company = result.scalars().first()
    if not company:
        raise HTTPException(status_code=404, detail="Kompaniya topilmadi")
    return serialize_company(company)


# ─── POST sync-external ─────────────────────────────────────────────────────────
@router.post("/sync-external")
async def sync_external_companies(db: AsyncSession = Depends(get_db)):
    """
    Tashqi API dan kompaniyalarni ko'chirib olib, bazaga yozish uchun maxsus endpoint.
    Bu yerda siz o'zingizning tashqi serveringiz manzilini (URL) va parolini (Header) yozasiz.
    """
    import asyncio
    import json
    import httpx
    
    # ⬇️ SHU YERGA O'ZINGIZNING EXTERNAL URL VA HEADER LARINI YOZING ⬇️
    EXTERNAL_API_URL = "https://developer.uyqur.uz/dev/company/info-for-bot"  
    EXTERNAL_HEADERS = {
        "Authorization": "header 'X-Auth: KmuWyVtwBA2rPunnbwTVW5NYXl$eWlPSIsInZhbHVlI'", 
        "Content-Type": "application/json"
    }
    # ⬆️ YUQORIDAGI O'ZGARUVCHILARNI ALMASHTIRING ⬆️

    try:
        # 1. Tashqi tizimga Request (API Fetch) jo'natish
        async with httpx.AsyncClient() as client:
            response = await client.get(EXTERNAL_API_URL, headers=EXTERNAL_HEADERS, timeout=10.0)
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Tashqi server xatosi: {response.status_code}")
                
            data = response.json()
            
        # 2. Kelgan datani (JSON) Array (ro'yxat) deb faraz qilib analiz qilamiz.
        # Agar JSON Object ichida ro'yxat kelsa "data": [...] unga moslash kerak.
        companies_list = data if isinstance(data, list) else data.get("data", [])
        
        if not companies_list:
            return {"status": "success", "message": "Tashqi bazada hech qanday yangi kompaniya topilmadi yoki data formati boshqacha."}
            
        added_count = 0
        
        for ext_company in companies_list:
            # 3. Ulardagi xossalarni bizning bazamizga to'g'rilab olish
            name = str(ext_company.get("name") or ext_company.get("company_name") or "Noma'lum Kompaniya")
            
            # Bazamizda xuddi shu ismli kompaniya bormi tekshirish (Double copy bo'lmasligi uchun)
            existing = await db.execute(select(Company).filter(Company.name == name))
            if existing.scalars().first():
                continue # Agar bo'lsa uni o'tkazib yuboradi
                
            phone = str(ext_company.get("phone") or ext_company.get("phone_number") or ext_company.get("contact") or "")
            director = str(ext_company.get("director") or ext_company.get("owner") or "")
            
            new_comp = Company(
                name=name,
                phone=phone if phone else None,
                director=director if director else None,
                status="Yangi",
                is_active=True
            )
            db.add(new_comp)
            added_count += 1
            
        await db.commit()
        
        return {
            "status": "success",
            "message": f"Muvaffaqiyatli ulangan! Jami {added_count} ta YANGI kompaniya bazaga qo'shildi."
        }
        
    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"Tashqi tizimga ulanishda xatolik: {exc}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xatolik yuz berdi: {e}")

# ─── POST create ──────────────────────────────────────────────────────────────
@router.post("/")
async def create_company(
    name: str = Form(...),
    brand_name: Optional[str] = Form(None),
    main_currency: str = Form("UZS"),
    extra_currency: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    director: Optional[str] = Form(None),
    responsible_name: Optional[str] = Form(None),
    responsible_phone: Optional[str] = Form(None),
    status: str = Form("Yangi"),
    subscription_start: Optional[str] = Form(None),
    subscription_end: Optional[str] = Form(None),
    is_active: bool = Form(True),
    logo: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    # Phone validation
    phone = validate_phone(phone)
    responsible_phone = validate_phone(responsible_phone)

    # Logo validation + upload
    logo_url = None
    if logo and logo.filename:
        content_type = logo.content_type or ""
        if content_type not in ALLOWED_MIME:
            raise HTTPException(status_code=422, detail=f"Logo formati qabul qilinmaydi: {content_type}. Ruxsat etilganlar: JPEG, PNG, WebP, GIF, SVG")

        contents = await logo.read()
        if len(contents) > MAX_LOGO_SIZE:
            raise HTTPException(status_code=422, detail="Logo hajmi 5MB dan oshmasligi kerak")

        # Pillow orqali rasm validatsiyasi (agar o'rnatilgan bo'lsa)
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(contents))
            img.verify()
        except ImportError:
            pass  # Pillow yo'q bo'lsa, MIME+size tekshiruvi yetarli
        except Exception:
            raise HTTPException(status_code=422, detail="Yuklangan fayl rasm emas yoki buzilgan")

        ext = os.path.splitext(logo.filename)[-1].lower() or ".png"
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        logo_url = f"/logos/{filename}"

    # Date parsing
    sub_start = datetime.fromisoformat(subscription_start) if subscription_start else None
    sub_end = datetime.fromisoformat(subscription_end) if subscription_end else None

    company = Company(
        name=name.strip(),
        logo_url=logo_url,
        brand_name=brand_name.strip() if brand_name else None,
        main_currency=main_currency.strip().upper(),
        extra_currency=extra_currency.strip().upper() if extra_currency else None,
        phone=phone,
        director=director.strip() if director else None,
        responsible_name=responsible_name.strip() if responsible_name else None,
        responsible_phone=responsible_phone,
        status=status,
        subscription_start=sub_start,
        subscription_end=sub_end,
        is_active=is_active,
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return serialize_company(company)


# ─── PUT update ───────────────────────────────────────────────────────────────
@router.put("/{company_id}")
async def update_company(
    company_id: int,
    name: str = Form(...),
    brand_name: Optional[str] = Form(None),
    main_currency: str = Form("UZS"),
    extra_currency: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    director: Optional[str] = Form(None),
    responsible_name: Optional[str] = Form(None),
    responsible_phone: Optional[str] = Form(None),
    status: str = Form("Yangi"),
    subscription_start: Optional[str] = Form(None),
    subscription_end: Optional[str] = Form(None),
    is_active: bool = Form(True),
    logo: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Company).filter(Company.id == company_id))
    company = result.scalars().first()
    if not company:
        raise HTTPException(status_code=404, detail="Kompaniya topilmadi")

    phone = validate_phone(phone)
    responsible_phone = validate_phone(responsible_phone)

    # Logo update
    if logo and logo.filename:
        content_type = logo.content_type or ""
        if content_type not in ALLOWED_MIME:
            raise HTTPException(status_code=422, detail=f"Logo formati qabul qilinmaydi: {content_type}")

        contents = await logo.read()
        if len(contents) > MAX_LOGO_SIZE:
            raise HTTPException(status_code=422, detail="Logo hajmi 5MB dan oshmasligi kerak")

        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(contents))
            img.verify()
        except ImportError:
            pass
        except Exception:
            raise HTTPException(status_code=422, detail="Yuklangan fayl rasm emas yoki buzilgan")

        # Eski logoni o'chirish
        if company.logo_url:
            old_path = os.path.join(UPLOAD_DIR, os.path.basename(company.logo_url))
            if os.path.exists(old_path):
                os.remove(old_path)

        ext = os.path.splitext(logo.filename)[-1].lower() or ".png"
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        company.logo_url = f"/logos/{filename}"

    company.name = name.strip()
    company.brand_name = brand_name.strip() if brand_name else None
    company.main_currency = main_currency.strip().upper()
    company.extra_currency = extra_currency.strip().upper() if extra_currency else None
    company.phone = phone
    company.director = director.strip() if director else None
    company.responsible_name = responsible_name.strip() if responsible_name else None
    company.responsible_phone = responsible_phone
    company.status = status
    company.subscription_start = datetime.fromisoformat(subscription_start) if subscription_start else None
    company.subscription_end = datetime.fromisoformat(subscription_end) if subscription_end else None
    company.is_active = is_active

    await db.commit()
    await db.refresh(company)
    return serialize_company(company)


# ─── PATCH toggle active ───────────────────────────────────────────────────────
@router.patch("/{company_id}/toggle")
async def toggle_company_active(company_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).filter(Company.id == company_id))
    company = result.scalars().first()
    if not company:
        raise HTTPException(status_code=404, detail="Kompaniya topilmadi")
    company.is_active = not company.is_active
    await db.commit()
    return {"id": company.id, "is_active": company.is_active}


# ─── DELETE ───────────────────────────────────────────────────────────────────
@router.delete("/{company_id}")
async def delete_company(company_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).filter(Company.id == company_id))
    company = result.scalars().first()
    if not company:
        raise HTTPException(status_code=404, detail="Kompaniya topilmadi")

    # Logo faylini o'chirish
    if company.logo_url:
        old_path = os.path.join(UPLOAD_DIR, os.path.basename(company.logo_url))
        if os.path.exists(old_path):
            os.remove(old_path)

    await db.delete(company)
    await db.commit()
    return {"status": "success", "message": "Kompaniya o'chirildi"}
