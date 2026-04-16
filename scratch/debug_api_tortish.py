import asyncio
import httpx
import json

# ⬇️ TASHQI BAZAGA ULANISH PAROLLARI ⬇️
EXTERNAL_API_URL = "https://developer.uyqur.uz/dev/company/info-for-bot"
EXTERNAL_HEADERS = {
    "X-Auth": "KmuWyVtwBA2rPunnbwTVW5NYXl$eWlPSIsInZhbHVlI",
    "Content-Type": "application/json"
}

async def debug_fetch():
    print("\n⏳ Tashqi serverga ulanish boshlandi...")
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(EXTERNAL_API_URL, headers=EXTERNAL_HEADERS, timeout=15.0)
            if response.status_code != 200:
                print(f"❌ Xatolik: Status {response.status_code}")
                return
            data = response.json()
            companies = data if isinstance(data, list) else data.get("data", [])
            print(f"✅ Ulandi! Jami {len(companies)} ta kompaniya.")
            
            # Print the first 3 companies in detail
            for i, c in enumerate(companies[:3]):
                print(f"\n--- COMPANY {i+1} RAW ---")
                print(json.dumps(c, indent=2))
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import json
    asyncio.run(debug_fetch())
