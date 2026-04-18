import asyncio
import os
import sys
sys.path.append(os.getcwd())

from bot.db import SessionLocal
from bot.models import Setting
from sqlalchemy import select, update
from bot.ai import get_ai_answer_async

async def test_kb_only():
    async with SessionLocal() as db:
        # Enable KB Only Mode
        await db.execute(update(Setting).where(Setting.key == "kb_only_mode").values(value="true"))
        await db.commit()
        
        print("Testing with KB Only Mode = TRUE and NO context...")
        res = await get_ai_answer_async("What is the capital of Japan?", context=None)
        print(f"Result: '{res['text']}'")
        
        if "NOT_FOUND" in res['text']:
            print("✅ Success: AI correctly returned NOT_FOUND")
        else:
            print("❌ Failure: AI did not return NOT_FOUND")

        # Test with context
        print("\nTesting with context...")
        res_context = await get_ai_answer_async("Where is the office?", context="The office is located in Tashkent, Amir Temur street.")
        print(f"Result: '{res_context['text']}'")
        if "Tashkent" in res_context['text']:
            print("✅ Success: AI correctly answered from context")
        else:
            print("❌ Failure: AI failed to use context")

        # Revert setting
        await db.execute(update(Setting).where(Setting.key == "kb_only_mode").values(value="false"))
        await db.commit()

if __name__ == "__main__":
    asyncio.run(test_kb_only())
