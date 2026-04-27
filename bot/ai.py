import os
import json
from pathlib import Path
from openai import OpenAI, AsyncOpenAI
import google.generativeai as genai
import warnings
# Google deprecated warningini vaqtinchalik o'chirib turish (FutureWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
from dotenv import load_dotenv
from bot.db import SessionLocal
from bot.models import Setting


load_dotenv()


async def get_db_setting(key: str, default: str = "") -> str:
    async with SessionLocal() as db:
        try:
            from sqlalchemy import select
            result = await db.execute(select(Setting).filter(Setting.key == key))
            setting = result.scalars().first()
            return setting.value if setting else default
        finally:
            await db.close()

def detect_question(text: str) -> bool:
    """Keyword-based question and help request detection (Fast)."""
    if not text:
        return False
    
    # 1. Belgilar orqali (Signs)
    if "?" in text:
        return True
    
    # 2. O'zbekcha savol qo'shimchalari (-mi, -chi, -a, -mikan, -mikin)
    text_lower = text.lower().strip()
    import re
    if re.search(r'(\w+mi|\w+-mi|\w+chi|\w+-chi|\w+-a|\w+mikan|\w+mikin)\b', text_lower):
        return True

    # 3. Savol va yordam so'zlari (Uzbek & Russian)
    question_keywords = [
        "nima", "qanday", "nega", "qachon", "kim", "qancha", "qaysi", "qanaqa", 
        "nechta", "qayerda", "nimaga", "qilib", "qilsam", "aytib", "bering",
        "narxi", "puli", "nechpul", "necha pul", "qancha turadi", "to'lov", "rassrochka", 
        "bo'lib to'lash", "kredit", "ipoteka", "manzil", "joylashuvi", "lokatsiya", 
        "kvadrat", "maydoni", "xona", "etaj", "qavat", "lift", "dokument", 
        "shartnoma", "kadastr", "propiska", "bitsa", "tugaydi", "srok",
        "bormi", "qolganmi", "sotildimi", "tashrif", "ko'rsat", "ko'rsa", "ko'ray",
        "yordam", "maslahat", "tushuntir", "ayt", "gapir", "muammo", "xato", "ishlamayapti",
        "что", "как", "почему", "когда", "кто", "сколько", "какой", "где", "зачем",
        "цена", "стоимость", "стоит", "оплата", "рассрочка", "кредит", "ипотека",
        "адрес", "локация", "квадрат", "метраж", "этаж", "комнат", "документ", 
        "договор", "кадастр", "сдача", "готов", "есть ли", "можно ли",
        "помоги", "совет", "объясни", "подскажи", "ошибка", "проблема", "не работает"
    ]
    
    # 4. Uzunlik va boshqa filtrlar
    if len(text_lower) < 3:
        return False
        
    return any(kw in text_lower for kw in question_keywords) or "?" in text_lower

async def is_question_ai(text: str) -> bool:
    """AI-based verification to see if the message is worth responding (Smart)."""
    # 1. Avval tezkor filtrdan o'tkazamiz
    if detect_question(text):
        return True
    
    # 2. Agar noaniq bo'lsa, AI dan juda qisqa so'raymiz
    provider = await get_db_setting("ai_provider", "openai")
    prompt = (
        "Siz 'UyQur' ko'chmas mulk kompaniyasi uchun savollarni aniqlash tizimisiz.\n"
        "VAZIFA: Foydalanuvchi xabarini tahlil qiling va u AI yordamchi yoki sotuvchi menejer javobiga muhtojmi yoki yo'qligini aniqlang.\n\n"
        "QUYIDAGI HOLLARDA 'TRUE' QAYTARING:\n"
        "- Agar xabar savol bo'lsa (narxi, manzili, shartlar haqida).\n"
        "- Agar yordam yoki ma'lumot so'ralgan bo'lsa.\n"
        "- Agar muammo yoki shikoyat haqida yozilgan bo'lsa.\n"
        "- Agar mulkni ko'rish yoki sotib olish istagi bildirilgan bo'lsa.\n\n"
        "QUYIDAGI HOLLARDA 'FALSE' QAYTARING:\n"
        "- Salomlashish (Salom, Assalomu alaykum).\n"
        "- Minnatdorchilik (Rahmat, Thanks).\n"
        "- Shunchaki gap yoki fikr (Masalan: 'Yaxshi ekan', 'Zo'r qurishibdi').\n"
        "- Ijtimoiy suhbatlar (Qalay, Nima gap).\n\n"
        "JUDA QAT'IY BO'LING: Faqat javob talab qiladigan xabarlarga 'TRUE' deb javob bering.\n"
        "FAQAT 'TRUE' YOKI 'FALSE' SO'ZINI QAYTARING."
    )
    
    try:
        if provider == "groq":
            api_key = await get_db_setting("groq_api_key", os.getenv("GROQ_API_KEY", ""))
            client = AsyncOpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            response = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}],
                max_tokens=5
            )
            return "TRUE" in response.choices[0].message.content.upper()
        
        elif provider == "gemini":
            api_key = await get_db_setting("gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=prompt)
            response = await model.generate_content_async(text)
            return "TRUE" in response.text.upper()
            
        else: # Default OpenAI
            api_key = await get_db_setting("openai_api_key", os.getenv("OPENAI_API_KEY", ""))
            client = AsyncOpenAI(api_key=api_key)
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}],
                max_tokens=5
            )
            return "TRUE" in response.choices[0].message.content.upper()
    except:
        return False

async def get_ai_answer_async(question: str, context: str = None) -> str:
    # 1. Sozlamalarni DB dan olish
    provider = await get_db_setting("ai_provider", "openai")
    custom_system_prompt = await get_db_setting("system_prompt", "")
    company_info = await get_db_setting("company_info", "")
    kb_only_mode = await get_db_setting("kb_only_mode", "false")

    # 2. System Promptni shakllantirish
    if context:
        if kb_only_mode == "true":
            system_prompt = (
                "Sen foydali yordamchi botsan. Vazifang: FAQAT quyidagi MAXSUS BAZA ma'lumotlaridan foydalanib javob berish. "
                "O'zingning umumiy bilimlaringni aslo ishlatma. Baza ichida bir nechta turli ma'lumotlar bo'lishi mumkin, "
                "ulardan foydalanib eng to'g'ri va to'liq javobni shakllantir. "
                "Agar savolga javob ushbu bazada bo'lmasa, FAQAT 'NOT_FOUND' so'zini qaytar.\n\n"
                f"MAXSUS BAZA (Bir nechta manbalar):\n{context}"
            )
        else:
            system_prompt = (
                "Sen foydali, xushmuomala yordamchi botsan. Quyida senga maxsus o'rgatilgan (Knowledge Base) tayyor bilimlar berilgan. "
                "Senga bir nechta manbalardan parchalar berilishi mumkin, ulardan foydalanib foydalanuvchiga yordam ber.\n"
                "Mavzu IT yoki boshqa soha bo'lishidan QAT'IY NAZAR, agar ushbu maxsus baza o'zida mos javobni ishora qilsa, o'shandan foydalan. "
                "Agar ma'lumot yetarli bo'lmasa, o'zingning umumiy bilimlaring bilan to'ldirishing mumkin.\n\n"
                f"Kompaniya haqida umumiy ma'lumot: {company_info}\n\n"
                f"Senga o'rgatilgan MAXSUS BAZA ma'lumotlari:\n{context}"
            )
    elif custom_system_prompt:
        system_prompt = f"{custom_system_prompt}\n\nKompaniya ma'lumotlari: {company_info}"
        if kb_only_mode == "true":
             system_prompt += "\nMUHIM: Agar javob senga berilgan ma'lumotlarda bo'lmasa, FAQAT 'NOT_FOUND' qaytar."
    else:
        if kb_only_mode == "true":
            system_prompt = (
                "Sen FAQAT kompaniya ma'lumotlari va bilimlar bazasi asosida javob beradigan botsan. "
                "O'zingning umumiy bilimlaringni ishlatma. Agar javob topilmasa, FAQAT 'NOT_FOUND' so'zini qaytar.\n"
                f"Kompaniya ma'lumotlari: {company_info}"
            )
        else:
            system_prompt = (
                "Sen jahondagi eng yuqori malakali, aqlli va professional AI yordamchisan. "
                f"Kompaniya ma'lumotlari: {company_info}\n"
                "Sening vazifang: Har qanday mavzuda foydalanuvchi savollariga aniq, lisoniy to'g'ri va foydali javob berish! "
                "Agar savolga javob berish uchun maxsus bazada ma'lumot bo'lmasa, o'zingning umumiy bilimlaringdan foydalan."
            )

    try:
        # 3. Provayderga qarab so'rov yuborish
        if provider == "groq":
            api_key = await get_db_setting("groq_api_key", os.getenv("GROQ_API_KEY", ""))
            client = AsyncOpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            response = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": question}]
            )
            return {
                "text": response.choices[0].message.content,
                "usage": {
                    "provider": "groq",
                    "model": response.model,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }

        elif provider == "gemini":
            api_key = await get_db_setting("gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)
            response = await model.generate_content_async(question)
            
            # Gemini tokenlarini olish
            prompt_tokens = response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0
            completion_tokens = response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
            
            return {
                "text": response.text,
                "usage": {
                    "provider": "gemini",
                    "model": "gemini-1.5-flash", # Hozircha statik, lekin modelni sozlamadan olsa bo'ladi
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                }
            }

        else: # Default: OpenAI
            api_key = await get_db_setting("openai_api_key", os.getenv("OPENAI_API_KEY", ""))
            client = AsyncOpenAI(api_key=api_key)
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": question}]
            )
            return {
                "text": response.choices[0].message.content,
                "usage": {
                    "provider": "openai",
                    "model": response.model,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }

    except Exception as e:
        print(f"AI Error ({provider}):", e)
        return {
            "text": "",  # Xatolikni ko'rsatmaslik uchun bo'sh matn qaytaramiz
            "usage": None
        }


# Transcription functionality removed as per user request


# Sinxron versiya o'chirildi, chunki bot to'liq asinxron bo'ldi.