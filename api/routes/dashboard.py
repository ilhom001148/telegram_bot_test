from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from bot.db import SessionLocal
from bot.models import Group, Message
from bot.crud import get_ai_usage_stats, get_ai_usage_by_groups

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    try:
        # Guruhlar sonini nomi bo'yicha (distinct) sanaymiz
        total_groups_result = await db.execute(select(func.count(Group.title.distinct())))
        total_groups = total_groups_result.scalar() or 0
        
        # Statistikalar
        # 1. Jami xabarlar (Faqat userlar + Staff)
        total_messages_result = await db.execute(select(func.count(Message.id)))
        total_messages = total_messages_result.scalar() or 0
        
        # 2. Jami xabarlar (Faqat userlar)
        total_messages_no_staff_result = await db.execute(select(func.count(Message.id)).filter(Message.is_staff == False))
        total_messages_no_staff = total_messages_no_staff_result.scalar() or 0
        
        total_users_result = await db.execute(select(func.count(Message.user_id.distinct())))
        total_users = total_users_result.scalar() or 0

        total_questions_result = await db.execute(
            select(func.count(Message.id))
            .filter(Message.is_question == True, Message.is_staff == False)
        )
        total_questions = total_questions_result.scalar() or 0

        answered_questions_result = await db.execute(
            select(func.count(Message.id))
            .filter(
                Message.is_question == True,
                Message.is_staff == False,
                Message.is_answered == True
            )
        )
        answered_questions = answered_questions_result.scalar() or 0

        unanswered_questions_result = await db.execute(
            select(func.count(Message.id))
            .filter(
                Message.is_question == True,
                Message.is_staff == False,
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
            .filter(Message.is_question == True, Message.is_answered == False, Message.is_staff == False)
            .order_by(Message.id.desc())
            .limit(15)
        )
        latest_unanswered_raw = latest_unanswered_query.all()

        unanswered_formatted = []
        for msg, grp in latest_unanswered_raw:
            # Manually link group to msg for property usage
            msg.group = grp
            unanswered_formatted.append({
                "id": msg.id,
                "text": msg.text,
                "full_name": msg.full_name,
                "group_title": grp.title if grp else "Noma'lum",
                "telegram_link": msg.telegram_link,
                "telegram_app_link": msg.telegram_app_link,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })

        # Eng faol guruhni nomi bo'yicha topamiz
        most_active_group_query = await db.execute(
            select(Group.title, func.count(Message.id).label('msg_count'))
            .join(Message, Group.id == Message.group_id)
            .group_by(Group.title)
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
            .filter(Message.is_question == True, Message.is_staff == False)
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
                recent_qs_query = await db.execute(
                    select(Message.text)
                    .filter(Message.is_question == True, Message.is_staff == False)
                    .order_by(Message.id.desc())
                    .limit(50)
                )
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
                         api_key = await get_setting(db, "openai_api_key", os.getenv("OPENAI_API_KEY", ""))
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
            date = datetime.utcnow() - timedelta(days=i)
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            msgs_count_result = await db.execute(select(func.count(Message.id)).filter(Message.created_at >= start_date, Message.created_at <= end_date))
            msgs_count = msgs_count_result.scalar() or 0
            
            qs_count_result = await db.execute(select(func.count(Message.id)).filter(Message.is_question == True, Message.created_at >= start_date, Message.created_at <= end_date))
            qs_count = qs_count_result.scalar() or 0
            
            daily_activity.append({"day": date.strftime("%a"), "messages": msgs_count, "questions": qs_count})

        # Top 5 guruhlarni nomi bo'yicha birlashtirib chiqaramiz
        top_groups_query = await db.execute(
            select(Group.title, func.count(Message.id).label('msg_count'), func.sum(Message.total_tokens).label('token_count'))
            .join(Message, Group.id == Message.group_id)
            .group_by(Group.title)
            .order_by(func.count(Message.id).desc())
            .limit(5)
        )
        top_groups = top_groups_query.all()
        top_groups_formatted = [{"title": g[0], "messages": g[1], "tokens": g[2] or 0} for g in top_groups]

        # AI Usage Stats with Group Breakdown (Title bo'yicha)
        ai_usage_raw = await get_ai_usage_stats(db)
        ai_usage_by_groups = await get_ai_usage_by_groups(db)
        
        ai_usage_formatted = []
        for row in ai_usage_raw:
            provider = row[0]
            # Nomi bo'yicha yig'ish
            groups_map = {}
            for g in ai_usage_by_groups:
                if g[0] == provider:
                    title = g[1]
                    tokens = g[2] or 0
                    groups_map[title] = groups_map.get(title, 0) + tokens
            
            groups_for_provider = [{"title": t, "tokens": tk} for t, tk in groups_map.items()]
            
            ai_usage_formatted.append({
                "provider": provider,
                "tokens": row[1],
                "requests": row[2],
                "groups": sorted(groups_for_provider, key=lambda x: x['tokens'], reverse=True)
            })

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
            "top_groups": top_groups_formatted,
            "ai_usage": ai_usage_formatted
        }

    finally:
        # Dependency Depends(get_db) will handle session closure
        pass

@router.get("/support-stats")
async def get_support_stats(db: AsyncSession = Depends(get_db), period: str = "1_week"):
    try:
        from sqlalchemy import cast, Integer, or_, func
        from datetime import datetime, timedelta, timezone
        from sqlalchemy.orm import joinedload
        from bot.models import Group
        
        now = datetime.now(timezone.utc)
        start_date = None
        
        if period == "1_day":
            start_date = now - timedelta(days=1)
        elif period == "3_days":
            start_date = now - timedelta(days=3)
        elif period == "1_week":
            start_date = now - timedelta(days=7)
        elif period == "1_month":
            start_date = now - timedelta(days=30)
            
        def apply_date_filter(query, date_column):
            if start_date:
                return query.filter(date_column >= start_date)
            return query
            
        base_q_cond = [Message.is_question == True, Message.is_staff == False]
        
        # 1. Top Metrics
        q_tot = select(func.count(Message.id)).filter(*base_q_cond)
        total_tickets = await db.scalar(apply_date_filter(q_tot, Message.created_at)) or 0
        
        q_res = select(func.count(Message.id)).filter(*base_q_cond, Message.is_answered == True)
        resolved_tickets = await db.scalar(apply_date_filter(q_res, Message.answered_at)) or 0
        
        resolve_rate = round((resolved_tickets / total_tickets * 100), 1) if total_tickets > 0 else 0
        
        q_groups = select(func.count(Message.id)).join(Group, Message.group_id == Group.id).filter(*base_q_cond, Group.telegram_id < 0)
        from_groups = await db.scalar(apply_date_filter(q_groups, Message.created_at)) or 0
        
        q_avg = select(Message.created_at, Message.answered_at).filter(*base_q_cond, Message.is_answered == True, Message.answered_at != None)
        avg_res = await db.execute(apply_date_filter(q_avg, Message.answered_at))
        valid_diffs = []
        for c_at, a_at in avg_res.all():
            if c_at and a_at:
                # Ikkalasini ham naive qilish orqali solishtiramiz
                c_naive = c_at.replace(tzinfo=None) if c_at.tzinfo else c_at
                a_naive = a_at.replace(tzinfo=None) if a_at.tzinfo else a_at
                diff = (a_naive - c_naive).total_seconds()
                if diff > 0 and diff < 86400 * 30: # ignore future or absurdly old
                    valid_diffs.append(diff)
        
        avg_time_sec = sum(valid_diffs) / len(valid_diffs) if valid_diffs else 0
        avg_response_minutes = round((avg_time_sec / 60), 1) if avg_time_sec else 0
        
        # 2. Periods Breakdown
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        bugun = await db.scalar(select(func.count(Message.id)).filter(*base_q_cond, Message.created_at >= today_start)) or 0
        hafta = await db.scalar(select(func.count(Message.id)).filter(*base_q_cond, Message.created_at >= week_start)) or 0
        oy = await db.scalar(select(func.count(Message.id)).filter(*base_q_cond, Message.created_at >= month_start)) or 0
        jami = await db.scalar(select(func.count(Message.id)).filter(*base_q_cond)) or 0
        periods = {"bugun": bugun, "hafta": hafta, "oy": oy, "jami": jami}
        
        # 3. Sources
        guruh = await db.scalar(apply_date_filter(select(func.count(Message.id)).join(Group, Message.group_id == Group.id).filter(*base_q_cond, Group.telegram_id < 0), Message.created_at)) or 0
        shaxsiy = await db.scalar(apply_date_filter(select(func.count(Message.id)).join(Group, Message.group_id == Group.id).filter(*base_q_cond, Group.telegram_id > 0), Message.created_at)) or 0
        sources = {"guruh": guruh, "shaxsiy": shaxsiy}
        
        # 4. Agent Stats & Top Agents
        q_replies = apply_date_filter(select(Message).filter(
            Message.is_question == False,
            Message.reply_to_message_id != None,
            or_(Message.full_name.ilike("%uyqur%"), Message.username.ilike("%uyqur%"), Message.full_name == "Admin (AI Panel)")
        ), Message.created_at)
        replies_res = await db.execute(q_replies)
        replies = replies_res.scalars().all()
        
        agent_data = {}
        for r in replies:
            name = r.full_name or "Noma'lum"
            if name not in agent_data:
                agent_data[name] = {"username": r.username, "resolved": 0, "unique_qs": set(), "chats": set(), "times": [], "last": r.created_at}
            
            if r.reply_to_message_id and r.reply_to_message_id not in agent_data[name]["unique_qs"]:
                agent_data[name]["resolved"] += 1
                agent_data[name]["unique_qs"].add(r.reply_to_message_id)
                
            agent_data[name]["chats"].add(r.group_id)
            if r.created_at > agent_data[name]["last"]:
                agent_data[name]["last"] = r.created_at
                
        # Bot Stats
        q_bot = apply_date_filter(select(Message).filter(Message.is_question == True, Message.answered_by_bot == True), Message.answered_at)
        bot_res = await db.execute(q_bot)
        bot_answers = bot_res.scalars().all()
        if bot_answers:
            bot_name = "AI Bot (Auto)"
            answered_times = [b.answered_at for b in bot_answers if b.answered_at]
            # Vaqtlarni bir xillashtiramiz (naive/aware muammosini oldini olish uchun)
            normalized_times = [t.replace(tzinfo=timezone.utc) if not t.tzinfo else t for t in answered_times]
            agent_data[bot_name] = {
                "username": "bot", 
                "resolved": len(bot_answers), 
                "chats": set([b.group_id for b in bot_answers]), 
                "times": [], 
                "last": max(normalized_times) if normalized_times else now
            }

        # Match questions to calculate agent avg response time
        reply_ids = [r.reply_to_message_id for r in replies if r.reply_to_message_id]
        if reply_ids:
            q_qs = select(Message.group_id, Message.telegram_message_id, Message.created_at).filter(Message.telegram_message_id.in_(reply_ids), Message.is_question == True)
            qs_res = await db.execute(q_qs)
            qs_dict = {(row[0], row[1]): row[2] for row in qs_res.all()}
            for r in replies:
                key = (r.group_id, r.reply_to_message_id)
                if key in qs_dict and r.created_at:
                    q_time = qs_dict[key]
                    # Ikkalasi ham aware ekanligiga ishonch hosil qilamiz
                    r_at = r.created_at if r.created_at.tzinfo else r.created_at.replace(tzinfo=timezone.utc)
                    q_at = q_time if q_time.tzinfo else q_time.replace(tzinfo=timezone.utc)
                    diff = (r_at - q_at).total_seconds()
                    if diff >= 0 and diff < 86400 * 30: # Limit to max 30 days
                        agent_data[r.full_name or "Noma'lum"]["times"].append(diff)
                        
        top_agents = []
        agent_stats = []
        total_agent_resolved = sum([d["resolved"] for d in agent_data.values()])
        for name, data in agent_data.items():
            avg_t = sum(data["times"]) / len(data["times"]) / 60 if data["times"] else 0
            
            # Calculate SLA (percentage of responses within 30 minutes)
            within_sla = len([t for t in data["times"] if t <= 1800])
            sla = round((within_sla / len(data["times"]) * 100), 1) if data["times"] else 100
            
            # Determine Rating
            rating = "C"
            if sla >= 95: rating = "A+"
            elif sla >= 85: rating = "A"
            elif sla >= 70: rating = "B"
            
            share = round((data["resolved"] / total_agent_resolved * 100), 1) if total_agent_resolved > 0 else 0
            agent_stats.append({
                "name": name,
                "username": data["username"] or "",
                "resolved": data["resolved"],
                "share": share,
                "chats": len(data["chats"]),
                "avg_time": round(avg_t, 1),
                "sla": sla,
                "rating": rating,
                "last_resolved": data["last"].isoformat() if data["last"] else None
            })
            top_agents.append({"name": name, "resolved": data["resolved"]})
            
        top_agents = sorted(top_agents, key=lambda x: x['resolved'], reverse=True)[:5]
        agent_stats = sorted(agent_stats, key=lambda x: x['resolved'], reverse=True)
        
        # 5. Active Groups
        q_act_grp = apply_date_filter(select(Group.title, func.count(Message.id)).join(Group, Message.group_id == Group.id).filter(*base_q_cond, Group.telegram_id < 0), Message.created_at)
        q_act_grp = q_act_grp.group_by(Group.title).order_by(func.count(Message.id).desc()).limit(5)
        act_grp_res = await db.execute(q_act_grp)
        active_groups = [{"name": row[0], "total": row[1]} for row in act_grp_res.all()]
        
        # 6. Open Tickets
        q_open = select(Message, Group).join(Group, Message.group_id == Group.id).filter(*base_q_cond, Message.is_answered == False)
        q_open = q_open.order_by(Message.created_at.desc()).limit(10)
        open_res = await db.execute(q_open)
        open_tickets = []
        for msg, grp in open_res.all():
            open_tickets.append({
                "id": msg.id,
                "client": msg.full_name or msg.username or "Noma'lum",
                "source": grp.title if grp.telegram_id < 0 else "Shaxsiy",
                "text": msg.text or "",
                "time": msg.created_at.isoformat() if msg.created_at else None,
                "telegram_app_link": msg.telegram_app_link
            })
            
        # 7. Group Stats Table
        q_grp_stats = apply_date_filter(select(
            Group.title, 
            func.count(Message.id).label('tot'),
            func.sum(cast(Message.is_answered, Integer)).label('res'),
            func.count(func.distinct(Message.user_id)).label('users'),
            func.max(Message.created_at).label('last'),
            Group.telegram_id,
            Group.username
        ).join(Group, Message.group_id == Group.id).filter(*base_q_cond, Group.telegram_id < 0), Message.created_at)
        q_grp_stats = q_grp_stats.group_by(Group.title, Group.telegram_id, Group.username).order_by(func.count(Message.id).desc()).limit(15)
        grp_stats_res = await db.execute(q_grp_stats)
        group_stats = []
        for title, tot, res, users, last, t_id, username in grp_stats_res.all():
            opn = tot - (res or 0)
            rr = round(((res or 0) / tot * 100), 1) if tot > 0 else 0
            
            link = "#"
            if username:
                link = f"tg://resolve?domain={username.lstrip('@')}"
            elif t_id:
                c_id = str(t_id)
                if c_id.startswith("-100"): c_id = c_id[4:]
                link = f"https://t.me/c/{c_id}/999999999"

            group_stats.append({
                "name": title,
                "total": tot,
                "open": opn,
                "resolved": res or 0,
                "resolve_rate": rr,
                "users": users,
                "last_question": last.isoformat() if last else None,
                "link": link
            })
            
        # 8. Overall Agent Statistics
        q_all_replies = select(Message).filter(
            Message.is_question == False,
            Message.reply_to_message_id != None,
            or_(Message.full_name.ilike("%uyqur%"), Message.username.ilike("%uyqur%"), Message.full_name == "Admin (AI Panel)")
        )
        all_replies_res = await db.execute(q_all_replies)
        all_replies = all_replies_res.scalars().all()
        
        all_agent_data = {}
        for r in all_replies:
            name = r.full_name or "Noma'lum"
            if name not in all_agent_data:
                all_agent_data[name] = {"username": r.username, "received": 0, "resolved": 0, "unique_qs": set(), "last": r.created_at, "times": []}
                
            all_agent_data[name]["received"] += 1
            if r.reply_to_message_id and r.reply_to_message_id not in all_agent_data[name]["unique_qs"]:
                all_agent_data[name]["resolved"] += 1
                all_agent_data[name]["unique_qs"].add(r.reply_to_message_id)
                
            if r.created_at > all_agent_data[name]["last"]:
                all_agent_data[name]["last"] = r.created_at
                
        all_reply_ids = [r.reply_to_message_id for r in all_replies if r.reply_to_message_id]
        if all_reply_ids:
            q_all_qs = select(Message.group_id, Message.telegram_message_id, Message.created_at).filter(Message.telegram_message_id.in_(all_reply_ids), Message.is_question == True)
            all_qs_res = await db.execute(q_all_qs)
            all_qs_dict = {(row[0], row[1]): row[2] for row in all_qs_res.all()}
            for r in all_replies:
                key = (r.group_id, r.reply_to_message_id)
                if key in all_qs_dict and r.created_at:
                    q_time = all_qs_dict[key]
                    # Ikkalasi ham aware ekanligiga ishonch hosil qilamiz
                    r_at = r.created_at if r.created_at.tzinfo else r.created_at.replace(tzinfo=timezone.utc)
                    q_at = q_time if q_time.tzinfo else q_time.replace(tzinfo=timezone.utc)
                    diff = (r_at - q_at).total_seconds()
                    if diff >= 0 and diff < 86400 * 30:
                        all_agent_data[r.full_name or "Noma'lum"]["times"].append(diff)
                        
        agent_overall_stats = []
        for name, data in all_agent_data.items():
            avg_t = round(sum(data["times"]) / len(data["times"]) / 60, 1) if data["times"] else 0
            
            # Calculate SLA (percentage of responses within 30 minutes)
            within_sla = len([t for t in data["times"] if t <= 1800])
            sla = round((within_sla / len(data["times"]) * 100), 1) if data["times"] else 100
            
            # Determine Rating
            rating = "C"
            if sla >= 95: rating = "A+"
            elif sla >= 85: rating = "A"
            elif sla >= 70: rating = "B"
            
            agent_overall_stats.append({
                "name": name,
                "username": data["username"] or "",
                "received": data["received"],
                "resolved": data["resolved"],
                "avg_time": avg_t,
                "sla": sla,
                "rating": rating,
                "last_resolved": data["last"].isoformat() if data["last"] else None
            })
        agent_overall_stats = sorted(agent_overall_stats, key=lambda x: x['resolved'], reverse=True)

        return {
            "top_metrics": {
                "total_tickets": total_tickets,
                "resolved_tickets": resolved_tickets,
                "unanswered_tickets": total_tickets - resolved_tickets,
                "resolve_rate": resolve_rate,
                "from_groups": from_groups,
                "avg_response_minutes": avg_response_minutes,
                "overdue_tickets": len([t for t in open_tickets if t["time"] and (datetime.utcnow() - datetime.fromisoformat(t["time"])).total_seconds() > 1800]) if open_tickets else 0
            },
            "periods": periods,
            "sources": sources,
            "top_agents": top_agents,
            "active_groups": active_groups,
            "agent_stats": agent_stats,
            "open_tickets": open_tickets,
            "group_stats": group_stats,
            "agent_overall_stats": agent_overall_stats
        }

    finally:
        pass

@router.get("/analytics")
async def get_comprehensive_analytics(db: AsyncSession = Depends(get_db), period: str = "1_week"):
    try:
        from sqlalchemy import cast, Integer, or_, func, case, distinct
        from datetime import datetime, timedelta
        from sqlalchemy.orm import joinedload
        from bot.models import Group, Company, Message, User
        
        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=7) # Default
        if period == "1_day": start_date = now - timedelta(days=1)
        elif period == "3_days": start_date = now - timedelta(days=3)
        elif period == "1_week": start_date = now - timedelta(days=7)
        elif period == "1_month": start_date = now - timedelta(days=30)
        elif period == "all": start_date = datetime(2000, 1, 1, tzinfo=timezone.utc)

        # Helper: Date filter
        def df(q, col=Message.created_at):
            return q.filter(col >= start_date)

        # 1. Support Performance Data
        base_q = [Message.is_question == True, Message.is_staff == False]
        
        total_tickets = await db.scalar(df(select(func.count(Message.id)).filter(*base_q))) or 0
        resolved_tickets = await db.scalar(df(select(func.count(Message.id)).filter(*base_q, Message.is_answered == True))) or 0
        
        # Trend
        prev_start = start_date - (now - start_date)
        prev_tickets = await db.scalar(select(func.count(Message.id)).filter(*base_q, Message.created_at >= prev_start, Message.created_at < start_date)) or 0
        
        if prev_tickets == 0 and total_tickets > 0:
            trend_str = "+100%"
        elif prev_tickets == 0 and total_tickets == 0:
            trend_str = "0%"
        else:
            trend_val = round(((total_tickets - prev_tickets) / prev_tickets * 100), 1)
            # Agar foiz juda katta bo'lib ketsa, limit qo'yamiz yoki butun qismini chiqaramiz
            if trend_val > 999:
                trend_str = f"+{round(total_tickets - prev_tickets)} ta"
            else:
                trend_str = f"{'+' if trend_val >= 0 else ''}{trend_val}%"
        
        # Overdue (>30m unanswered)
        overdue_q = df(select(func.count(Message.id)).filter(*base_q, Message.is_answered == False, Message.created_at < now - timedelta(minutes=30)))
        overdue_tickets = await db.scalar(overdue_q) or 0
        
        # Avg Response Time
        avg_res_q = await db.execute(df(select(Message.created_at, Message.answered_at).filter(*base_q, Message.is_answered == True, Message.answered_at != None)))
        diffs = [abs((r[1].replace(tzinfo=None) - r[0].replace(tzinfo=None)).total_seconds()) for r in avg_res_q.all() if r[0] and r[1]]
        avg_time = round(sum(diffs) / len(diffs) / 60, 1) if diffs else 0
        
        # 2. Product Analytics
        modules = ["Hisobot", "Ombor", "CRM", "To'lov", "Login", "API"]
        module_stats = {m: {"total": 0, "bug": 0, "feature": 0} for m in modules}
        
        msgs_q = await db.execute(df(select(Message.text).filter(Message.is_staff == False)))
        all_msg_texts = [r[0] for r in msgs_q.all() if r[0]]
        
        for text in all_msg_texts:
            found = False
            for m in modules:
                if m.lower() in text.lower():
                    module_stats[m]["total"] += 1
                    if any(k in text.lower() for k in ["xato", "ishlamayapti", "error", "bug", "muammo"]):
                        module_stats[m]["bug"] += 1
                    elif any(k in text.lower() for k in ["kerak", "qo'shish", "yangi", "taklif"]):
                        module_stats[m]["feature"] += 1
                    found = True
                    break
            if not found:
                if "Boshqa" not in module_stats: module_stats["Boshqa"] = {"total": 0, "bug": 0, "feature": 0}
                module_stats["Boshqa"]["total"] += 1

        prev_msgs_q = await db.execute(select(Message.text).filter(Message.is_staff == False, Message.created_at >= prev_start, Message.created_at < start_date))
        prev_texts = [r[0] for r in prev_msgs_q.all() if r[0]]
        
        prev_module_stats = {m: 0 for m in modules}
        for text in prev_texts:
            for m in modules:
                if m.lower() in text.lower():
                    prev_module_stats[m] += 1
                    break

        product_analytics = []
        for m, s in module_stats.items():
            if s["total"] > 0:
                prev_m = prev_module_stats.get(m, 0)
                if prev_m > 0:
                    tr = round((s["total"] - prev_m) / prev_m * 100)
                    if tr > 999: tr_str = f"+{s['total'] - prev_m} ta"
                    else: tr_str = f"+{tr}%" if tr > 0 else f"{tr}%"
                else:
                    tr_str = "+100%" if s["total"] > 0 else "0%"
                product_analytics.append({"module": m, "total": s["total"], "bug": s["bug"], "feature": s["feature"], "trend": tr_str})
        
        # 3. Company & Group Aggregation
        from api.routes.companies import get_external_companies
        ext_companies = await get_external_companies()
        local_comps_res = await db.execute(select(Company))
        local_companies = [{"name": c.name, "id": str(c.id), "status": c.status} for c in local_comps_res.scalars().all()]
        all_comps = local_companies + ext_companies
        
        groups_res = await db.execute(select(Group))
        all_groups = groups_res.scalars().all()
        
        # Performance by group
        msgs_by_grp = await db.execute(df(select(Message.group_id, func.count(Message.id), func.count(distinct(Message.user_id)), func.max(Message.created_at)).filter(Message.is_staff == False).group_by(Message.group_id)))
        grp_metrics = {r[0]: {"msgs": r[1], "users": r[2], "last": r[3]} for r in msgs_by_grp.all()}
        
        q_by_grp = await db.execute(df(select(Message.group_id, func.count(Message.id)).filter(*base_q).group_by(Message.group_id)))
        grp_q_counts = {r[0]: r[1] for r in q_by_grp.all()}
        
        a_by_grp = await db.execute(df(select(Message.group_id, func.count(Message.id)).filter(*base_q, Message.is_answered == True).group_by(Message.group_id)))
        grp_a_counts = {r[0]: r[1] for r in a_by_grp.all()}

        company_activity = []
        group_stats = []

        for comp in all_comps:
            c_name = comp.get("name", "")
            c_status = comp.get("status", "Yangi")
            c_groups = [g for g in all_groups if c_name.lower() in g.title.lower()]
            
            c_total_msgs = sum(grp_metrics.get(g.id, {}).get("msgs", 0) for g in c_groups)
            c_total_users = sum(grp_metrics.get(g.id, {}).get("users", 0) for g in c_groups)
            c_total_q = sum(grp_q_counts.get(g.id, 0) for g in c_groups)
            c_total_a = sum(grp_a_counts.get(g.id, 0) for g in c_groups)
            
            # Advanced Health Scoring
            health_score = 0
            reasons = []
            
            if c_total_users > 0:
                health_score += 30 # Baza: foydalanuvchi borligi uchun
                if c_total_users > 5: health_score += 20
                
                # Javob berish sifati (SLA)
                if c_total_q > 0:
                    res_rate = c_total_a / c_total_q
                    health_score += (res_rate * 50)
                    if res_rate < 0.5: reasons.append("Savollarning yarmidan ko'pi javobsiz")
                else:
                    health_score += 50 # Savol bo'lmasa, demak muammo yo'q
            else:
                reasons.append("Tizimda birorta ham faol foydalanuvchi yo'q")
                
            # Obuna muddati (agar mavjud bo'lsa)
            sub_end = comp.get("subscription_end")
            if sub_end:
                try:
                    from datetime import datetime
                    end_dt = datetime.fromisoformat(sub_end.replace("Z", ""))
                    days_left = (end_dt - datetime.utcnow()).days
                    if days_left < 0:
                        health_score -= 50
                        reasons.append("Obuna muddati tugagan")
                        c_status = "Muddati o'tgan"
                    elif days_left < 7:
                        health_score -= 20
                        reasons.append(f"Obuna {days_left} kunda tugaydi")
                except: pass

            # Final Status Determination
            final_status = c_status
            if health_score < 40: final_status = "Risk"
            elif health_score > 80: final_status = "Active"
            
            if c_total_msgs > 0 or c_status in ["Faol", "Active", "Yangi"]:
                company_activity.append({
                    "name": c_name,
                    "users": c_total_users,
                    "sessions": c_total_msgs,
                    "tickets": c_total_q,
                    "score": max(0, min(100, int(health_score))),
                    "status": final_status,
                    "reasons": reasons if reasons else ["Hozircha hamma ko'rsatkichlar me'yorda"]
                })
            
            for g in c_groups:
                m = grp_metrics.get(g.id, {})
                t = grp_q_counts.get(g.id, 0)
                a = grp_a_counts.get(g.id, 0)
                if t > 0 or m.get("msgs", 0) > 0:
                    group_stats.append({
                        "name": g.title,
                        "total": t,
                        "open": t - a,
                        "resolved": a,
                        "resolve_rate": round(a/t*100, 1) if t > 0 else 0,
                        "last_question": m.get("last").isoformat() if m.get("last") else None
                    })

        group_stats.sort(key=lambda x: x["total"], reverse=True)

        # 5. Agent Performance (Advanced Contextual Logic)
        from datetime import timedelta
        
        # 1. Fetch all relevant data for the period
        all_msgs_res = await db.execute(
            select(Message)
            .filter(Message.created_at >= start_date)
            .order_by(Message.chat_id, Message.created_at.asc())
        )
        all_msgs = all_msgs_res.scalars().all()
        
        # Group messages by chat_id
        chats = {}
        for m in all_msgs:
            if m.chat_id not in chats: chats[m.chat_id] = []
            chats[m.chat_id].append(m)
            
        agent_stats = {}
        
        for chat_id, msgs in chats.items():
            unanswered_qs = [] # Stack of questions waiting for answer
            
            for m in msgs:
                if m.is_question and not m.is_staff:
                    unanswered_qs.append(m)
                
                elif m.is_staff and not m.answered_by_bot:
                    name = m.full_name or "Noma'lum"
                    if name not in agent_stats:
                        agent_stats[name] = {"replies": 0, "total_time": 0, "matched": 0}
                    
                    agent_stats[name]["replies"] += 1
                    
                    # Try to match this staff message to a question
                    target_q = None
                    
                    # Priority 1: Direct Reply
                    if m.reply_to_message_id:
                        target_q = next((q for q in unanswered_qs if q.telegram_message_id == m.reply_to_message_id), None)
                    
                    # Priority 2: Smart Contextual Match (if no direct reply)
                    if not target_q and unanswered_qs:
                        # Take the most recent question
                        last_q = unanswered_qs[-1]
                        # Only match if within 6 hours
                        if (m.created_at - last_q.created_at).total_seconds() < 21600:
                            target_q = last_q
                    
                    if target_q:
                        diff = (m.created_at - target_q.created_at).total_seconds() / 60
                        agent_stats[name]["total_time"] += diff
                        agent_stats[name]["matched"] += 1
                        # Once answered, remove from unanswered stack
                        if target_q in unanswered_qs:
                            unanswered_qs.remove(target_q)

        agent_perf = []
        for name, s in agent_stats.items():
            if "uyqur" not in name.lower(): continue
            
            avg_m = round(s["total_time"] / s["matched"], 1) if s["matched"] > 0 else 0
            # SLA based on matched answers
            sla = 0
            if s["matched"] > 0:
                sla = 95 if avg_m < 15 else (85 if avg_m < 60 else 70)
            elif s["replies"] > 0:
                sla = 40 # Active but not using reply/slow
                
            grade = "A+" if avg_m > 0 and avg_m < 10 else "A" if avg_m < 30 else "B" if avg_m < 120 else "C"
            
            agent_perf.append({
                "name": name,
                "replies": s["replies"],
                "avg_time": f"{avg_m} min" if avg_m > 0 else "0 min",
                "sla": f"{sla}%",
                "grade": grade
            })
            
        agent_perf.sort(key=lambda x: x["replies"], reverse=True)

        # 6. Trend Analysis (Dynamic: Hourly for 1_day, Daily for others)
        if period == "1_day":
            hourly_res = await db.execute(df(select(func.extract('hour', Message.created_at).label('h'), func.count(Message.id)).filter(Message.is_staff == False).group_by('h').order_by('h')))
            hour_counts = {int(r[0]): r[1] for r in hourly_res.all()}
            trend_data = [{"label": f"{h:02d}:00", "value": hour_counts.get(h, 0)} for h in range(24)]
        else:
            # Daily grouping
            daily_res = await db.execute(df(select(func.date(Message.created_at).label('d'), func.count(Message.id)).filter(Message.is_staff == False).group_by('d').order_by('d')))
            trend_data = [{"label": r[0].strftime("%d-%b") if hasattr(r[0], 'strftime') else str(r[0]), "value": r[1]} for r in daily_res.all()]

        # Overdue Details
        overdue_details_q = await db.execute(df(select(Message.id, Message.full_name, Message.text, Message.created_at, Group.title).join(Group).filter(*base_q, Message.is_answered == False, Message.created_at < now - timedelta(minutes=30))))
        overdue_list = []
        for m_id, c_name, text, time, g_title in overdue_details_q.all():
            overdue_list.append({
                "id": m_id,
                "client": c_name or "Mijoz",
                "text": text if text else "",
                "time": time.isoformat(),
                "group": g_title,
                "wait": int((now.replace(tzinfo=None) - time.replace(tzinfo=None)).total_seconds() / 60)
            })

        return {
            "performance": {
                "today_tickets": total_tickets,
                "trend": trend_str,
                "resolved": resolved_tickets,
                "resolve_rate": f"{round(resolved_tickets/total_tickets*100, 1) if total_tickets > 0 else 0}%",
                "unanswered": total_tickets - resolved_tickets,
                "overdue": overdue_tickets,
                "overdue_list": overdue_list[:10],
                "avg_response": f"{avg_time} min"
            },
            "product": product_analytics,
            "companies": company_activity[:15],
            "group_stats": group_stats,
            "hourly_trend": trend_data, # Frontend expects hourly_trend name
            "agent_performance": agent_perf
        }
    except Exception as e:
        import traceback
        print(f"ANALYTICS ERROR: {e}")
        print(traceback.format_exc())
        return {"error": str(e)}
        import traceback
        print(f"Analytics Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent-answers")
async def get_agent_answers(agent_name: str, period: str = "all", db: AsyncSession = Depends(get_db)):
    try:
        from datetime import datetime, timedelta
        from sqlalchemy.orm import joinedload
        
        now = datetime.now(timezone.utc)
        start_date = None
        
        if period == "1_day":
            start_date = now - timedelta(days=1)
        elif period == "3_days":
            start_date = now - timedelta(days=3)
        elif period == "1_week":
            start_date = now - timedelta(days=7)
        elif period == "1_month":
            start_date = now - timedelta(days=30)
            
        if agent_name == "AI Bot (Auto)":
            q = select(Message).options(joinedload(Message.group)).filter(Message.is_question == True, Message.answered_by_bot == True)
            if start_date:
                q = q.filter(Message.answered_at >= start_date)
            q = q.order_by(Message.answered_at.desc()).limit(50)
            result = await db.execute(q)
            questions = result.scalars().all()
            
            items = []
            for q_obj in questions:
                grp = q_obj.group
                items.append({
                    "id": q_obj.id,
                    "group_title": grp.title if grp else "Noma'lum",
                    "question_text": q_obj.text,
                    "answer_text": "🤖 AI Avto-javob bergan (Matn saqlanmagan)",
                    "answered_at": q_obj.answered_at.isoformat() if q_obj.answered_at else None,
                    "telegram_app_link": q_obj.telegram_app_link
                })
            return {"agent_name": agent_name, "answers": items}
            
        else:
            # Human agent
            q_replies = select(Message).filter(
                Message.is_question == False,
                Message.full_name == agent_name,
                Message.reply_to_message_id != None
            )
            if start_date:
                q_replies = q_replies.filter(Message.created_at >= start_date)
                
            q_replies = q_replies.order_by(Message.created_at.desc()).limit(50)
            replies_res = await db.execute(q_replies)
            replies = replies_res.scalars().all()
            
            if not replies:
                return {"agent_name": agent_name, "answers": []}
                
            reply_dict = {r.reply_to_message_id: r for r in replies}
                
            q_questions = select(Message).options(joinedload(Message.group)).filter(
                Message.is_question == True,
                Message.telegram_message_id.in_(reply_dict.keys())
            )
            q_res = await db.execute(q_questions)
            questions_dict = {q.telegram_message_id: q for q in q_res.scalars().all()}
            
            items = []
            for r_id, reply_obj in reply_dict.items():
                if r_id in questions_dict:
                    q_obj = questions_dict[r_id]
                    grp = q_obj.group
                    items.append({
                        "id": q_obj.id,
                        "group_title": grp.title if grp else "Noma'lum",
                        "question_text": q_obj.text,
                        "answer_text": reply_obj.text,
                        "answered_at": reply_obj.created_at.isoformat() if reply_obj.created_at else None,
                        "telegram_app_link": q_obj.telegram_app_link
                    })
            # Sort items by answered_at descending
            items.sort(key=lambda x: x["answered_at"] or "", reverse=True)
            return {"agent_name": agent_name, "answers": items[:50]}
    finally:
        pass