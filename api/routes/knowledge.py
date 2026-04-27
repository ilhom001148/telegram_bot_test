from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from typing import List
import io
import os
import json
import docx2txt
from pypdf import PdfReader
from openai import AsyncOpenAI

from api.dependencies import get_db, get_current_admin
from bot.models import KnowledgeBase

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])

class KnowledgeCreate(BaseModel):
    question: str
    answer: str

class BulkKnowledgeCreate(BaseModel):
    items: List[KnowledgeCreate]

class KnowledgeResponse(BaseModel):
    id: int
    question: str
    answer: str
    
    class Config:
        from_attributes = True

def extract_text_from_file(file_path: str, filename: str) -> str:
    ext = filename.lower().split('.')[-1]
    if ext == 'pdf':
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        return text
    elif ext == 'docx':
        return docx2txt.process(file_path)
    elif ext == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise ValueError(f"Qo'llab-quvvatlanmaydigan fayl formati: {ext}")

def split_text_into_chunks(text: str, chunk_size: int = 4000, overlap: int = 400) -> List[str]:
    """Matnni bo'laklarga bo'lib beradi (Overlap bilan)."""
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

async def extract_knowledge_api(text: str, db: AsyncSession):
    # 1. Sozlamalarni DB dan olish
    from bot.crud import get_setting
    provider_raw = await get_setting(db, "ai_provider", "openai")
    provider = provider_raw.lower() if provider_raw else "openai"
    
    # 2. Matnni bo'laklarga bo'lish (Kichikroq chunklar = yaxshiroq detal)
    chunks = split_text_into_chunks(text, chunk_size=10000)
    all_extracted_knowledge = []
    
    prompt = (
        "Siz 'UyQur' ko'chmas mulk kompaniyasi uchun professional bilimlar bazasi mutaxassisiz.\n"
        "VAZIFA: Quyidagi matndan barcha muhim biznes ma'lumotlarini SAVOL va JAVOB shaklida ajratib oling.\n\n"
        "QUYIDAGI MA'LUMOTLARGA ALOHIDA E'TIBOR BERING:\n"
        "- Narxlar, kvadrat metrlari, qavatlar va binolar holati.\n"
        "- To'lov shartlari (rassrochka, kredit, ipoteka, chegirmalar, boshlang'ich to'lov).\n"
        "- Manzillar, lokatsiyalar va mo'ljallar.\n"
        "- Shartnoma tuzish tartibi, kerakli hujjatlar va kadastr ma'lumotlari.\n"
        "- Kompaniya qoidalari, ish vaqti va kontaktlar.\n\n"
        "JUDA DETALLASHGAN VA TO'LIQ BO'LSIN: Matndagi kichik detallarni ham savol-javobga aylantiring.\n"
        "MUHIM: JAVOBLARNI QISQARTIRMANG. Agar javob uzun bo'lsa ham, uni to'liq, boricha oling. Chala javoblar mutlaqo mumkin emas.\n"
        "FAQAT matnda bor ma'lumotlardan foydalaning. O'zingizdan ma'lumot qo'shmang.\n"
        "Natijani FAQAT JSON formatida qaytaring: {\"knowledge\": [{\"question\": \"...\", \"answer\": \"...\"}, ...]}"
    )

    for chunk in chunks:
        try:
            content = ""
            if provider == "groq":
                api_key = await get_setting(db, "groq_api_key", os.getenv("GROQ_API_KEY", ""))
                client = AsyncOpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1", timeout=120.0)
                response = await client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a professional knowledge extractor. Return only a JSON object with a 'knowledge' key containing a list of Q&A pairs."},
                        {"role": "user", "content": f"{prompt}\n\nTEXT CHUNK:\n{chunk}"}
                    ],
                    response_format={ "type": "json_object" },
                    max_tokens=4000
                )
                content = response.choices[0].message.content

            elif provider == "gemini":
                import google.generativeai as genai
                api_key = await get_setting(db, "gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = await model.generate_content_async(
                    f"{prompt}\n\nTEXT CHUNK:\n{chunk}",
                    generation_config={
                        "response_mime_type": "application/json",
                        "max_output_tokens": 4000
                    },
                    request_options={"timeout": 120}
                )
                content = response.text

            else: # OpenAI
                api_key = await get_setting(db, "openai_api_key", os.getenv("OPENAI_API_KEY", ""))
                client = AsyncOpenAI(api_key=api_key, timeout=120.0)
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a professional knowledge extractor. Return only a JSON object with a 'knowledge' key containing a list of Q&A pairs."},
                        {"role": "user", "content": f"{prompt}\n\nTEXT CHUNK:\n{chunk}"}
                    ],
                    response_format={ "type": "json_object" },
                    max_tokens=4000
                )
                content = response.choices[0].message.content

            # JSONni aqlli parslash
            data = json.loads(content)
            chunk_knowledge = []
            if isinstance(data, dict):
                if "knowledge" in data:
                    chunk_knowledge = data["knowledge"]
                elif "items" in data:
                    chunk_knowledge = data["items"]
                else:
                    # To'g'ridan-to'g'ri lug'at bo'lsa, qidirib ko'ramiz
                    for key in data:
                        if isinstance(data[key], list) and len(data[key]) > 0:
                            chunk_knowledge = data[key]
                            break
            elif isinstance(data, list):
                chunk_knowledge = data
            
            if chunk_knowledge:
                all_extracted_knowledge.extend(chunk_knowledge)

        except Exception as e:
            print(f"Extraction Chunk Error ({provider}): {str(e)}")
            continue # Bitta bo'lak xato bersa, keyingisiga o'tamiz
            
    return all_extracted_knowledge

@router.get("/", response_model=List[KnowledgeResponse])
async def get_knowledge_list(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(KnowledgeBase).order_by(KnowledgeBase.id.desc()))
    return result.scalars().all()

@router.post("/", response_model=KnowledgeResponse)
async def create_knowledge(item: KnowledgeCreate, db: AsyncSession = Depends(get_db)):
    kb = KnowledgeBase(question=item.question, answer=item.answer)
    db.add(kb)
    await db.commit()
    await db.refresh(kb)
    return kb

@router.post("/bulk")
async def bulk_create_knowledge(data: BulkKnowledgeCreate, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    for item in data.items:
        kb = KnowledgeBase(question=item.question, answer=item.answer)
        db.add(kb)
    await db.commit()
    return {"status": "success", "count": len(data.items)}

@router.post("/extract")
async def extract_knowledge_from_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    temp_path = f"temp_{file.filename}"
    try:
        # 1. Faylni vaqtincha saqlash
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # 2. Matnni ajratib olish
        text = extract_text_from_file(temp_path, file.filename)
        
        if not text or len(text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Fayldan yetarli matn topilmadi.")

        # 3. AI orqali tahlil qilish
        knowledge = await extract_knowledge_api(text, db)
        
        return knowledge

    except Exception as e:
        print(f"Extraction Error: {e}")
        raise HTTPException(status_code=500, detail=f"Faylni tahlil qilishda xatolik: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.put("/{kb_id}", response_model=KnowledgeResponse)
async def update_knowledge(kb_id: int, item: KnowledgeCreate, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(KnowledgeBase).filter(KnowledgeBase.id == kb_id))
    kb = result.scalars().first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    
    kb.question = item.question
    kb.answer = item.answer
    
    await db.commit()
    await db.refresh(kb)
    return kb

@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge(kb_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(KnowledgeBase).filter(KnowledgeBase.id == kb_id))
    kb = result.scalars().first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    
    await db.delete(kb)
    await db.commit()
    return None
