import httpx
import json

EXTERNAL_API_URL = "https://developer.uyqur.uz/dev/company/info-for-bot"
EXTERNAL_HEADERS = {
    "X-Auth": "KmuWyVtwBA2rPunnbwTVW5NYXl$eWlPSIsInZhbHVlI",
    "Content-Type": "application/json"
}

def test_fetch():
    print(f"Connecting to {EXTERNAL_API_URL}...")
    try:
        response = httpx.get(EXTERNAL_API_URL, headers=EXTERNAL_HEADERS, timeout=10.0)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Data received successfully!")
            # Print first 2 items as sample
            sample = data if isinstance(data, list) else data.get("data", [])
            print(f"Total items: {len(sample)}")
            if sample:
                print("First item sample:")
                print(json.dumps(sample[0], indent=2, ensure_ascii=False))
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_fetch()
