import os
import re
import uuid
import shutil
import httpx
import json
import time
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.dependencies import get_db
from bot.models import Company
from typing import Optional, List

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

# ─── 24-soatlik kesh (DB ga saqlanmaydi, xotirada saqlanadi) ─────────────────
_ext_cache = {"data": [], "fetched_at": 0}
CACHE_TTL = 86400  # 24 soat (soniyada)

OVERRIDES_FILE = "data/external_overrides.json"
os.makedirs("data", exist_ok=True)

def load_overrides():
    if not os.path.exists(OVERRIDES_FILE):
        return {}
    try:
        with open(OVERRIDES_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_override(comp_id: str, is_active: bool):
    overrides = load_overrides()
    overrides[comp_id] = is_active
    with open(OVERRIDES_FILE, "w") as f:
        json.dump(overrides, f)

# ─── GET external live ────────────────────────────────────────────────────────
@router.get("/external")
async def get_external_companies():
    global _ext_cache

    # ─── Kesh 24 soatdan yangi bo'lsa shu zahoti qaytaramiz ───────────────────
    now_ts = time.time()
    if _ext_cache["fetched_at"] and (now_ts - _ext_cache["fetched_at"]) < CACHE_TTL:
        print(f"⚡ [Cache] Keshdagi {len(_ext_cache['data'])} ta kompaniya qaytarilmoqda (yangi API so'rovsiz)")
        return _ext_cache["data"]

    # ─── Kesh eskirgan — Tashqi API dan yangi ma'lumot olish ─────────────────
    print("🔄 [Cache] 24 soat o'tdi yoki birinchi yuklash — Tashqi API dan tortilmoqda...")
    url = "https://developer.uyqur.uz/dev/company/info-for-bot"
    headers = {
        "X-Auth": "KmuWyVtwBA2rPunnbwTVW5NYXl$eWlPSIsInZhbHVlI",
        "Content-Type": "application/json",
        "User-Agent": "curl/7.68.0"
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=headers, timeout=20.0)
            if response.status_code != 200:
                # Kesh mavjud bo'lsa eski ma'lumotni qaytaramiz
                if _ext_cache["data"]:
                    print(f"⚠️ [Cache] Tashqi API javobi {response.status_code} — eski kesh qaytarilmoqda")
                    return _ext_cache["data"]
                raise HTTPException(status_code=502, detail=f"Tashqi API xatosi: {response.status_code}")
            
            raw_data = response.json()
            if isinstance(raw_data, list):
                companies_list = raw_data
            elif isinstance(raw_data, dict):
                companies_list = raw_data.get("data") or raw_data.get("companies") or raw_data.get("list")
                if companies_list is None:
                    for val in raw_data.values():
                        if isinstance(val, list) and len(val) > 0:
                            companies_list = val
                            break
                    else: companies_list = []
            else: companies_list = []
            
            results = []
            for i, c in enumerate(companies_list):
                try:
                    if not isinstance(c, dict): continue

                    # 1. Obuna muddati (Date)
                    exp_raw = c.get("expired") or c.get("subscription_end") or c.get("expires_at")
                    iso_expired = None
                    if exp_raw and isinstance(exp_raw, str):
                        if "." in exp_raw:
                            try:
                                parts = exp_raw.split('.')[:3]
                                if len(parts) == 3:
                                    d, m, y = parts
                                    iso_expired = f"{y}-{m}-{d}T00:00:00"
                            except: pass
                        elif "-" in exp_raw: iso_expired = exp_raw

                    # 2. Kompaniya nomi
                    comp_name = (
                        c.get("name") or c.get("company_name") or 
                        c.get("title") or c.get("brand_name") or 
                        c.get("brand") or c.get("company") or 
                        c.get("business_name") or c.get("org_name") or
                        f"Kompaniya #{c.get('id') or i}"
                    )

                    # 3. Mas'ul xodim
                    resp_name = (
                        c.get("responsible_name") or c.get("uyqur_support_username") or
                        c.get("staff_name") or c.get("support_name") or
                        c.get("agent_name") or c.get("manager_name") or
                        c.get("owner_name") or c.get("director") or
                        c.get("responsible_person") or c.get("contact_person") or
                        c.get("responsible") or c.get("staff") or
                        c.get("agent") or c.get("manager") or "Noma'lum"
                    )

                    # 4. Telefon raqamlari
                    resp_phone = (
                        c.get("responsible_phone") or c.get("uyqur_support_phone") or
                        c.get("staff_phone") or c.get("support_phone") or
                        c.get("agent_phone") or c.get("manager_phone") or
                        c.get("phone_1") or c.get("mobile") or
                        c.get("contact_phone") or c.get("phone") or ""
                    )
                    comp_phone = (
                        c.get("phone") or c.get("phone_number") or
                        c.get("contact") or c.get("contact_phone") or
                        c.get("company_phone") or resp_phone or "Mavjud emas"
                    )

                    # 5. Logo
                    logo = c.get("logo_url") or c.get("image") or c.get("logo") or c.get("avatar") or None

                    # 6. Status & Overrides
                    now_str = datetime.now().isoformat()
                    base_status = str(c.get("status") or "").lower()
                    is_active_api = bool(c.get("is_real") or c.get("is_active") or base_status == "active")
                    
                    comp_id = f"ext-{c.get('id') or i}"
                    
                    # Apply local overrides
                    overrides = load_overrides()
                    is_active = is_active_api
                    if comp_id in overrides:
                        is_active = overrides[comp_id]

                    if iso_expired and iso_expired < now_str:
                        calc_status = "To'xtatilgan"
                    elif base_status in ["canceled", "cancelled", "deleted", "inactive"]:
                        calc_status = "Bekor qilingan"
                    elif is_active:
                        calc_status = "Faol"
                    else:
                        calc_status = "Yangi"

                    results.append({
                        "id": comp_id,
                        "name": comp_name,
                        "brand_name": c.get("brand_name") or c.get("brand") or "",
                        "phone": comp_phone,
                        "director": c.get("director") or c.get("owner") or c.get("leader") or "",
                        "responsible_name": resp_name,
                        "responsible_phone": resp_phone,
                        "subscription_start": c.get("created_at") or c.get("start_date") or None,
                        "subscription_end": iso_expired or exp_raw or None,
                        "status": calc_status,
                        "is_active": is_active,
                        "logo_url": logo,
                        "main_currency": c.get("currency") or "UZS",
                    })
                except Exception as item_err:
                    print(f"DEBUG Skipping item {i}: {str(item_err)}")
                    continue

            # ─── Keshni yangilash ─────────────────────────────────────────────
            _ext_cache["data"] = results
            _ext_cache["fetched_at"] = now_ts
            print(f"✅ [Cache] {len(results)} ta kompaniya keshlandi")
            return results

    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG Error in /external: {str(e)}")
        # Kesh mavjud bo'lsa eski ma'lumotni qaytaramiz
        if _ext_cache["data"]:
            print("⚠️ [Cache] Xatolik — eski kesh qaytarilmoqda")
            return _ext_cache["data"]
        raise HTTPException(status_code=500, detail=f"Ulanishda xatolik: {str(e)}")


# ─── GET all (Local) ──────────────────────────────────────────────────────────
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

    if logo and logo.filename:
        content_type = logo.content_type or ""
        if content_type not in ALLOWED_MIME:
            raise HTTPException(status_code=422, detail=f"Logo formati qabul qilinmaydi: {content_type}")
        contents = await logo.read()
        if len(contents) > MAX_LOGO_SIZE:
            raise HTTPException(status_code=422, detail="Logo hajmi 5MB dan oshmasligi kerak")
        
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
async def toggle_company_active(company_id: str, db: AsyncSession = Depends(get_db)):
    if company_id.startswith("ext-"):
        # Handle External Persistence
        overrides = load_overrides()
        # Find current state in cache
        current_state = True
        for c in _ext_cache["data"]:
            if c["id"] == company_id:
                current_state = c["is_active"]
                break
        
        new_state = not current_state
        save_override(company_id, new_state)
        
        # Update cache immediately for feedback
        for c in _ext_cache["data"]:
            if c["id"] == company_id:
                c["is_active"] = new_state
                # Update status text
                if new_state: c["status"] = "Faol"
                else: c["status"] = "Nofaol"
                break
                
        return {"id": company_id, "is_active": new_state}
    
    # Handle Local DB Persistence
    try:
        cid_int = int(company_id)
        result = await db.execute(select(Company).filter(Company.id == cid_int))
        company = result.scalars().first()
        if not company:
            raise HTTPException(status_code=404, detail="Kompaniya topilmadi")
        company.is_active = not company.is_active
        await db.commit()
        return {"id": company.id, "is_active": company.is_active}
    except ValueError:
        raise HTTPException(status_code=400, detail="ID noto'g'ri formatda")

# ─── DELETE ───────────────────────────────────────────────────────────────────
@router.delete("/{company_id}")
async def delete_company(company_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).filter(Company.id == company_id))
    company = result.scalars().first()
    if not company:
        raise HTTPException(status_code=404, detail="Kompaniya topilmadi")

    if company.logo_url:
        old_path = os.path.join(UPLOAD_DIR, os.path.basename(company.logo_url))
        if os.path.exists(old_path):
            os.remove(old_path)

    await db.delete(company)
    await db.commit()
    return {"status": "success", "message": "Kompaniya o'chirildi"}
