from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from bot.db import SessionLocal
from bot.models import Group, Message

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    try:
        total_groups_result = await db.execute(select(func.count(Group.id)))
        total_groups = total_groups_result.scalar() or 0
        
        total_messages_result = await db.execute(select(func.count(Message.id)))
        total_messages = total_messages_result.scalar() or 0
        
        total_users_result = await db.execute(select(func.count(Message.user_id.distinct())))
        total_users = total_users_result.scalar() or 0

        total_questions_result = await db.execute(
            select(func.count(Message.id))
            .filter(Message.is_question == True)
        )
        total_questions = total_questions_result.scalar() or 0

        answered_questions_result = await db.execute(
            select(func.count(Message.id))
            .filter(
                Message.is_question == True,
                Message.is_answered == True
            )
        )
        answered_questions = answered_questions_result.scalar() or 0

        unanswered_questions_result = await db.execute(
            select(func.count(Message.id))
            .filter(
                Message.is_question == True,
                Message.is_answered == False
            )
        )
        unanswered_questions = unanswered_questions_result.scalar() or 0

        bot_answers_result = await db.execute(
            select(func.count(Message.id))
            .filter(
                Message.answered_by_bot == True
            )
        )
        bot_answers = bot_answers_result.scalar() or 0

        latest_unanswered_query = await db.execute(
            select(Message, Group)
            .join(Group, Message.group_id == Group.id)
            .filter(Message.is_question == True, Message.is_answered == False)
            .order_by(Message.id.desc())
            .limit(5)
        )
        latest_unanswered_raw = latest_unanswered_query.all()

        unanswered_formatted = []
        for msg, grp in latest_unanswered_raw:
            telegram_link = None
            if grp:
                if grp.username:
                    username = grp.username.lstrip('@')
                    telegram_link = f"https://t.me/{username}/{msg.telegram_message_id}"
                elif grp.telegram_id:
                    chat_id_str = str(grp.telegram_id)
                    if chat_id_str.startswith("-100"):
                        chat_id_str = chat_id_str[4:]
                    telegram_link = f"https://t.me/c/{chat_id_str}/{msg.telegram_message_id}"

            unanswered_formatted.append({
                "id": msg.id,
                "text": msg.text,
                "full_name": msg.full_name,
                "group_title": grp.title if grp else "Noma'lum",
                "telegram_link": telegram_link,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })

        most_active_group_query = await db.execute(
            select(Group.title, func.count(Message.id).label('msg_count'))
            .join(Message, Group.id == Message.group_id)
            .group_by(Group.id, Group.title)
            .order_by(func.count(Message.id).desc())
            .limit(1)
        )
        most_active_group_raw = most_active_group_query.first()

        most_active_group = {
            "title": most_active_group_raw[0] if most_active_group_raw else "N/A",
            "messages": most_active_group_raw[1] if most_active_group_raw else 0
        }

        most_active_user_query = await db.execute(
            select(Message.full_name, Message.username, func.count(Message.id).label('q_count'))
            .filter(Message.is_question == True)
            .group_by(Message.user_id, Message.full_name, Message.username)
            .order_by(func.count(Message.id).desc())
            .limit(1)
        )
        most_active_user_raw = most_active_user_query.first()

        most_active_user = {
            "full_name": most_active_user_raw[0] if most_active_user_raw else "N/A",
            "username": most_active_user_raw[1] if most_active_user_raw else None,
            "count": most_active_user_raw[2] if most_active_user_raw else 0
        }

        # AI-Powered Trending Topics (Semantic Clustering) - Multi-provider (ASYNCHRONOUS)
        import os, json, time
        from bot.crud import get_setting
        
        provider_raw = await get_setting(db, "ai_provider", "openai")
        provider = provider_raw.lower() if provider_raw else "openai"
        
        # Global cache for topics
        if 'topics_cache' not in globals():
            globals()['topics_cache'] = {"data": [], "timestamp": 0}
        
        current_time = time.time()
        # Cache for 1 hour (3600 seconds)
        if current_time - globals()['topics_cache']["timestamp"] < 3600 and globals()['topics_cache']["data"]:
            trending_formatted = globals()['topics_cache']["data"]
        else:
            try:
                recent_qs_query = await db.execute(select(Message.text).filter(Message.is_question == True).order_by(Message.id.desc()).limit(50))
                recent_qs = recent_qs_query.all()
                if not recent_qs:
                    trending_formatted = []
                else:
                    qs_list = "\n".join([f"- {q[0]}" for q in recent_qs[:50]])
                    prompt = (
                        "Analyze these questions and group them into the top 5 most frequent themes. "
                        "Return only a JSON object like: {\"topics\": [{\"word\": \"Theme Name\", \"count\": number}]}. "
                        f"Questions:\n{qs_list}"
                    )
                    
                    content = ""
                    if provider == "groq":
                         from openai import AsyncOpenAI
                         api_key = await get_setting(db, "groq_api_key", os.getenv("GROQ_API_KEY", ""))
                         client = AsyncOpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
                         response = await client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
                         content = response.choices[0].message.content
                    elif provider == "gemini":
                         import google.generativeai as genai
                         api_key = await get_setting(db, "gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
                         genai.configure(api_key=api_key)
                         model = genai.GenerativeModel('gemini-1.5-flash')
                         response = await model.generate_content_async(prompt, generation_config={"response_mime_type": "application/json"})
                         content = response.text
                    else: # OpenAI
                         from openai import AsyncOpenAI
                         api_key = await get_setting(db, "openai_api_key", os.getenv("OPEN_AI_API_KEY", ""))
                         client = AsyncOpenAI(api_key=api_key)
                         response = await client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
                         content = response.choices[0].message.content

                    ai_data = json.loads(content)
                    trending_formatted = ai_data.get("topics", [])[:5]
                    globals()['topics_cache'] = {"data": trending_formatted, "timestamp": current_time}
            except Exception as e:
                print(f"AI Topic Analysis Error ({provider}): {e}")
                trending_formatted = []

        # Daily Activity for Chart (Last 7 days)
        from datetime import datetime, timedelta
        daily_activity = []
        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            msgs_count_result = await db.execute(select(func.count(Message.id)).filter(Message.created_at >= start_date, Message.created_at <= end_date))
            msgs_count = msgs_count_result.scalar() or 0
            
            qs_count_result = await db.execute(select(func.count(Message.id)).filter(Message.is_question == True, Message.created_at >= start_date, Message.created_at <= end_date))
            qs_count = qs_count_result.scalar() or 0
            
            daily_activity.append({"day": date.strftime("%a"), "messages": msgs_count, "questions": qs_count})

        # Top 5 most active groups for charts
        top_groups_query = await db.execute(
            select(Group.title, func.count(Message.id).label('msg_count'))
            .join(Message, Group.id == Message.group_id)
            .group_by(Group.id, Group.title)
            .order_by(func.count(Message.id).desc())
            .limit(5)
        )
        top_groups = top_groups_query.all()
        top_groups_formatted = [{"title": g[0], "messages": g[1]} for g in top_groups]

        return {
            "total_groups": total_groups,
            "total_messages": total_messages,
            "total_users": total_users,
            "total_questions": total_questions,
            "answered_questions": answered_questions,
            "unanswered_questions": unanswered_questions,
            "bot_answers": bot_answers,
            "latest_unanswered": unanswered_formatted,
            "most_active_group": most_active_group,
            "most_active_user": most_active_user,
            "trending_topics": trending_formatted,
            "daily_activity": daily_activity,
            "top_groups": top_groups_formatted
        }

    except Exception as e:
        import traceback
        print(f"DASHBOARD STATS ERROR: {e}")
        print(traceback.format_exc())
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "total_groups": 0,
            "total_messages": 0,
            "total_users": 0,
            "total_questions": 0,
            "answered_questions": 0,
            "unanswered_questions": 0,
            "bot_answers": 0,
            "latest_unanswered": [],
            "most_active_group": {"title": "N/A", "messages": 0},
            "most_active_user": {"full_name": "N/A", "username": None, "count": 0},
            "trending_topics": [],
            "daily_activity": [],
            "top_groups": []
        }
    finally:
        # Dependency Depends(get_db) will handle session closure
        pass