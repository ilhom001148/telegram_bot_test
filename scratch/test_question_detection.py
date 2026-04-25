import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot.ai import detect_question, is_question_ai

async def test_detection():
    test_cases = [
        # Questions (Should be TRUE)
        ("Narxi qancha?", True),
        ("Kvadrat metri necha puldan?", True),
        ("Manzilingiz qayerda?", True),
        ("Rassrochka bormi?", True),
        ("Shartnoma qilsak bo'ladimi?", True),
        ("Dokumentlari joyidami?", True),
        ("Qachon bitsa bo'ladi?", True),
        ("Assalomu alaykum, narxlarni bilsam bo'ladimi?", True),
        ("Сколько стоит 2-х комнатная квартира?", True),
        ("Где находится ваш офис?", True),
        ("Есть рассрочка?", True),
        
        # Statements/Social/Greetings (Should be FALSE)
        ("Salom", False),
        ("Assalomu alaykum yaxshimisizlar", False),
        ("Rahmat kattakon", False),
        ("Yaxshi ekan", False),
        ("Zo'r qurishibdi gap bo'lishi mumkin emas", False),
        ("Ishlaringizga omad", False),
        ("Привет всем", False),
        ("Спасибо за информацию", False),
    ]

    print(f"{'Xabar':<50} | {'Kutilgan':<10} | {'Natija':<10}")
    print("-" * 75)

    for text, expected in test_cases:
        # Fast keyword check
        kw_result = detect_question(text)
        
        # AI check (will use real API if keys are set)
        ai_result = await is_question_ai(text)
        
        # Final decision is what the bot uses (is_question_ai calls detect_question first)
        final_result = ai_result
        
        status = "✅" if final_result == expected else "❌"
        print(f"{text[:49]:<50} | {str(expected):<10} | {str(final_result):<10} {status} (KW: {kw_result})")

if __name__ == "__main__":
    asyncio.run(test_detection())
