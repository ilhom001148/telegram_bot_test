import os

file_path = r"c:\Users\Asus\Desktop\UySot\telegram_bot\api\routes\dashboard.py"
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
new_lines.append("from datetime import datetime, timedelta, timezone\n") # Add global import

for line in lines:
    # Skip local imports of datetime and timedelta
    if "from datetime import datetime, timedelta" in line:
        continue
    new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Dashboard imports cleaned up.")
