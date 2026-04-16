import httpx
import json

url = "https://developer.uyqur.uz/dev/company/info-for-bot"
headers = {
    "X-Auth": "KmuWyVtwBA2rPunnbwTVW5NYXl$eWlPSIsInZhbHVlI",
    "Content-Type": "application/json"
}

def debug_api():
    print("Fetching raw API sample...")
    try:
        with httpx.Client(follow_redirects=True) as client:
            r = client.get(url, headers=headers, timeout=15)
            data = r.json()
            companies = data if isinstance(data, list) else data.get("data", [])
            if companies:
                # Find a company that might be representative
                # Or just print the first 2
                print(f"Total Companies: {len(companies)}")
                print("\nSAMPLE 1 RAW KEYS:")
                print(json.dumps(companies[0], indent=2))
                if len(companies) > 1:
                    print("\nSAMPLE 2 RAW KEYS:")
                    print(json.dumps(companies[1], indent=2))
            else:
                print("No companies found in response.")
                print(f"RAW DATA: {data}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_api()
