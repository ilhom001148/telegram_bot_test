import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def detect_question(text: str) -> bool:
    if not text:
        return False

    question_words = [
        "?", "nima", "qanday", "nega", "qachon", "kim", "qancha", "qaysi", 
        "qanaqa", "nechta", "qayerda", "nimaga", "qilib", "ber", 
        "ishlamayapti", "chiqmayapti", "xato", "error", "bug", "maslahat", "yordam"
    ]
    text_lower = text.lower()

    return any(word in text_lower for word in question_words)


def get_ai_answer(question: str, context: str = None) -> str:
    if context:
        system_prompt = (
            "Sen foydali, xushmuomala yordamchi botsan. Quyida senga adminlar tomonidan maxsus o'rgatilgan (Knowledge Base) tayyor bilim berilgan. "
            "Mavzu IT yoki boshqa soha bo'lishidan QAT'IY NAZAR, agar ushbu maxsus baza o'zida foydalanuvchining savoliga mos javobni ishora qilsa, "
            "chiroyli va insonlardek qilib o'sha bilimlarni yetkaz. Hech qanday holatda 'IGNORE' qilib suhbatni e'tiborsiz qoldirma!\n\n"
            f"Senga o'rgatilgan MAXSUS BAZA ma'lumotlari:\n{context}"
        )
    else:
        # Original strict IT prompt
        system_prompt = (
            "Sen jahondagi eng yuqori malakali, professional Dasturlash, IT va Sun'iy Intellekt (AI) bo'yicha ekspert botsan. "
            "Sening yagona vazifang: har bir dasturlash tili (Python, JavaScript, Java, C++, Go, Rust, PHP va h.k), "
            "dasturiy arxitekturalar, bazalar, turli AI/ML modellari xaqida o'ta chuqur darajada va to'liq yordam berish! "
            "Xususan, berilgan savollarga iloji boricha 'best practice' darajasidagi toza va mukammal **kod namunalari (code snippets)** bilan, qadam-baqadam erinmasdan javob ber. "
            "MUHIM QOIDA: Agar foydalanuvchi yozgan narsaning DASTURLASH, IT YOKI TEXNOLOGIYAga umuman aloqasi bo'lmasa "
            "(masalan: kundalik suhbatlar, siyosat, taomlar, salomlashish), suhbatga aralashmaslik uchun mutlaqo xat yozma, faqatgina 'IGNORE' xabarini qaytar (uzr ham so'rama). "
            "Faqat IT va kod yozish haqidagina eng to'liq Full rejimda chiroyli javob qaytar."
        )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )
    return response.choices[0].message.content