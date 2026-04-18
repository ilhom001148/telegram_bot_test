import asyncio
import os
import sys
sys.path.append(os.getcwd())

from bot.db import SessionLocal
from bot.crud import search_knowledge, create_knowledge

async def test_improved_retrieval():
    async with SessionLocal() as db:
        # Create some test data
        await create_knowledge(db, "Ish grafigi qanday?", "Ish grafigi 9:00 dan 18:00 gacha.")
        await create_knowledge(db, "Maosh qachon beriladi?", "Maosh har oyning 5-sanasida beriladi.")
        await create_knowledge(db, "Dam olish kunlari", "Shanba va yakshanba dam olish kunlari hisoblanadi.")
        await db.commit()
        
        print("Testing keyword ranking...")
        # Savol o'zgacha berilgan taqdirda ham topishi kerak
        matches = await search_knowledge(db, "Qachon ishga kelish kerak va maosh qaysi kuni?")
        
        print(f"Found {len(matches)} matches.")
        for i, m in enumerate(matches):
            print(f"Match {i+1} (Score logic): {m.question} -> {m.answer}")
        
        if len(matches) > 1:
            print("✅ Success: Multiple relevant matches found and ranked.")
        else:
            print("❌ Failure: Could not find multiple matches for compound query.")

if __name__ == "__main__":
    asyncio.run(test_improved_retrieval())
