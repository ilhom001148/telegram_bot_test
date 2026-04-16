import asyncio
import httpx

url = 'https://developer.uyqur.uz/dev/company/list'
token = 'KmuWyVtwBA2rPunnbwTVW5NYXl$eWlPSIsInZhbHVlI'

async def test():
    async with httpx.AsyncClient(verify=False) as c:
        try:
            res = await c.get(url, headers={'X-Auth': token})
            print(f"[{url}] {res.status_code}: {res.text[:100]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(test())
