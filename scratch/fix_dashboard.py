import os

file_path = r"c:\Users\Asus\Desktop\UySot\telegram_bot\api\routes\dashboard.py"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: now = datetime.utcnow()
content = content.replace("now = datetime.utcnow()", "now = datetime.now(timezone.utc)")

# Fix 2: diff calculation
old_diff = "diff = (r.created_at - q_time).total_seconds()"
new_diff = """# Ikkalasi ham aware ekanligiga ishonch hosil qilamiz
                    r_at = r.created_at if r.created_at.tzinfo else r.created_at.replace(tzinfo=timezone.utc)
                    q_at = q_time if q_time.tzinfo else q_time.replace(tzinfo=timezone.utc)
                    diff = (r_at - q_at).total_seconds()"""
content = content.replace(old_diff, new_diff)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ File fixed via script.")
