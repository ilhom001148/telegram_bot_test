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
    if "?" in text or "!" in text: # ! ham ko'pincha yordam so'rashni bildiradi
        return True
    
    # 2. Savol va yordam so'zlari (Uzbek & Russian)
    question_keywords = [
        # Uzbek
        "nima", "qanday", "nega", "qachon", "kim", "qancha", "qaysi", "qanaqa", 
        "nechta", "qayerda", "nimaga", "qilib", "ber", "yordam", "maslahat",
        "ishlamayapti", "xato", "chiqmayapti", "error", "bug", "muammo", "tushunmadim",
        "tushuntir", "ayt", "gapir", "qilsam", "bo'ladi", "qilsa", "mumkin", "kerak",
        "bilmoqchi", "aytsangiz", "yordamingiz", "narxi", "qancha", "manzil", "qayer",
        # Russian
        "что", "как", "почему", "когда", "кто", "сколько", "какой", "где",
        "помоги", "совет", "ошибка", "проблема", "баг", "не работает", "почему",
        "скажи", "объясни", "подскажи", "цена", "адрес", "где находится"
    ]
    
    text_lower = text.lower().strip()
    words = text_lower.split()
    
    # Faqat bitta so'z bo'lsa va u savol bo'lmasa (masalan: "Salom")
    if len(words) <= 1 and not ("?" in text_lower):
        return False

    return any(word in text_lower for word in question_keywords)

async def is_question_ai(text: str) -> bool:
    """AI-based verification to see if the message is worth responding (Smart)."""
    # 1. Avval tezkor filtrdan o'tkazamiz
    if detect_question(text):
        return True
    
    # 2. Agar noaniq bo'lsa, AI dan juda qisqa so'raymiz
    provider = await get_db_setting("ai_provider", "openai")
    prompt = (
        "TASK: Analyze the user message and determine if it requires a helpful response from an AI assistant. "
        "Return 'TRUE' if the message is: a question, a help request, a technical problem report, or a request for a task. "
        "Return 'FALSE' if the message is: just a greeting (Salom/Hi), a thank you (Rahmat/Thanks), "
        "a simple agreement (Ok/Xo'p), social small talk, or random noise. "
        "Only respond with 'TRUE' or 'FALSE'."
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


async def transcribe_audio(file_path: str) -> str:
    """Ovozni matnga aylantirish — Cloud API (Groq yoki OpenAI)."""
    # STT faqat Cloud API orqali (Render free tier uchun lokal model sig'maydi)
    provider = await get_db_setting("ai_provider", "openai")
    stt_mode = await get_db_setting("stt_mode", "cloud")
    
    # 3. Cloud API (Fallback yoki Asosiy)
    try:
        if not os.path.exists(file_path):
            print(f"❌ XATO: Audio fayl topilmadi: {file_path}")
            return ""

        if provider == "groq":
            api_key = await get_db_setting("groq_api_key", os.getenv("GROQ_API_KEY", ""))
            if not api_key:
                print("❌ GROQ_API_KEY topilmadi!")
                return ""
                
            client = AsyncOpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            with open(file_path, "rb") as audio_file:
                transcription = await client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=audio_file
                )
            return transcription.text
            
        else: # Default OpenAI for Audio transcription
            api_key = await get_db_setting("openai_api_key", os.getenv("OPENAI_API_KEY", ""))
            if not api_key:
                print("❌ OPENAI_API_KEY topilmadi!")
                return ""
            client = AsyncOpenAI(api_key=api_key)
            
            with open(file_path, "rb") as audio_file:
                transcription = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return transcription.text

    except Exception as e:
        print(f"STT Cloud Error ({provider}):", e)
        return ""

# Sinxron versiya o'chirildi, chunki bot to'liq asinxron bo'ldi.