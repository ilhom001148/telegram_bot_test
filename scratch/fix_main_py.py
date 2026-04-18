import os

path = 'bot/main.py'
content = open(path, 'r', encoding='utf-8').read()

# Replace first occurence (already partially done or needs to be consistent)
target_old = """kb_match = await search_knowledge(db, text)
                context = kb_match.answer if kb_match else None"""

replacement = """kb_matches = await search_knowledge(db, text)
                context = None
                if kb_matches:
                    context = "\\n---\\n".join([f"Ma'lumot {i+1}:\\nSavol: {m.question}\\nJavob: {m.answer}" for i, m in enumerate(kb_matches)])"""

new_content = content.replace(target_old, replacement)

open(path, 'w', encoding='utf-8').write(new_content)
print("Successfully replaced.")
