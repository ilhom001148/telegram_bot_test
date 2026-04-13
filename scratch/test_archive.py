
import asyncio
import os
from sqlalchemy import select, func, cast, Date, Integer
from bot.db import SessionLocal, engine
from bot.models import Message, Group
from datetime import datetime

async def test_archive_endpoints():
    async with SessionLocal() as db:
        print("--- Testing /messages/archive/summary ---")
        try:
            stats_query = (
                select(
                    cast(Message.created_at, Date).label("date"),
                    func.count(Message.id).label("total"),
                    # func.sum(cast(Message.is_answered, Integer)) is what's in the route
                    func.sum(cast(Message.is_answered, Integer)).label("answered")
                )
                .filter(Message.is_question == True)
                .group_by(cast(Message.created_at, Date))
                .order_by(cast(Message.created_at, Date).desc())
            )
            res = await db.execute(stats_query)
            results = res.all()
            print(f"Found {len(results)} days in summary.")
            for r in results:
                print(f"Date: {r.date}, Total: {r.total}, Answered: {r.answered}")
            
            if results:
                test_date = str(results[0].date)
                print(f"\n--- Testing /messages/archive/questions-by-date/{test_date} ---")
                
                # Simple version of the query
                qs_query = (
                    select(Message)
                    .filter(Message.is_question == True)
                    .filter(cast(Message.created_at, Date) == datetime.strptime(test_date, "%Y-%m-%d").date())
                    .order_by(Message.id.desc())
                )
                qs_res = await db.execute(qs_query)
                questions = qs_res.scalars().all()
                print(f"Found {len(questions)} questions for {test_date}.")
                
        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(test_archive_endpoints())
