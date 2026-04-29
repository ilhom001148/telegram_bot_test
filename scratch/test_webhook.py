import requests
import json

url = "http://localhost:8000/webhook/bot"
payload = {
    "update_id": 999999,
    "message": {
        "message_id": 12345,
        "from": {
            "id": 12345678,
            "is_bot": False,
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser"
        },
        "chat": {
            "id": -10022334455,
            "title": "Test Group",
            "type": "supergroup"
        },
        "date": 1600000000,
        "text": "Salom, bu test xabari. Narxi qancha?"
    }
}

try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
