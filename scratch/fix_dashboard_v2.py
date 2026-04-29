import os

file_path = r"c:\Users\Asus\Desktop\UySot\telegram_bot\api\routes\dashboard.py"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 3: Normalize answered_times before max()
old_max = '"last": max(answered_times).replace(tzinfo=timezone.utc) if answered_times else now'
new_max = '''# Vaqtlarni bir xillashtiramiz (naive/aware muammosini oldini olish uchun)
                normalized_times = [t.replace(tzinfo=timezone.utc) if not t.tzinfo else t for t in answered_times]
                "last": max(normalized_times) if normalized_times else now'''
content = content.replace(old_max, new_max)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Dashboard normalization fixed.")
