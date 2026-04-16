import asyncio
import httpx

url = 'https://developer.uyqur.uz/dev/company/info-for-bot'
token = 'KmuWyVtwBA2rPunnbwTVW5NYXl$eWlPSIsInZhbHVlI'

async def test():
    async with httpx.AsyncClient() as c:
        headers = [
            {'X-Auth': token},
            {"X-Auth": f"{token}"},
            {'Authorization': f"header 'X-Auth: {token}'"},
        ]
        
        print("--- GET REQUESTS ---")
        for i, h in enumerate(headers):
            try:
                res = await c.get(url, headers=h)
                print(f"GET [{i+1}] {h}: {res.status_code} | {res.text[:100]}")
            except Exception as e:
                print(f"GET [{i+1}] Error: {e}")
                
        print("\n--- POST REQUESTS ---")
        for i, h in enumerate(headers):
            try:
                res = await c.post(url, headers=h)
                print(f"POST [{i+1}] {h}: {res.status_code} | {res.text[:100]}")
            except Exception as e:
                print(f"POST [{i+1}] Error: {e}")

if __name__ == '__main__':
    asyncio.run(test())
