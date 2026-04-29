import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bot.crud import create_access_token

try:
    token = create_access_token(data={"sub": "admin"}, expires_delta=None)
    res = requests.get("http://localhost:8000/dashboard/analytics?period=1_week", headers={"Authorization": f"Bearer {token}"})
    print(res.status_code)
    print(res.json())
except Exception as e:
    print(e)
