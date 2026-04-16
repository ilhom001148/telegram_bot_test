import asyncio
import httpx
import json

url = 'https://developer.uyqur.uz/dev/company/info-for-bot'
token = 'KmuWyVtwBA2rPunnbwTVW5NYXl$eWlPSIsInZhbHVlI'

async def test():
    async with httpx.AsyncClient(verify=False) as c:
        try:
            res = await c.get(url, headers={'X-Auth': token})
            data = res.json()
            print("KEYS IN JSON:", data.keys())
            
            if 'companies' in data:
                print("YES, 'companies' key exists!")
                print("Number of companies:", len(data['companies']))
                if len(data['companies']) > 0:
                    print("Sample:", data['companies'][0])
                    
            if 'data' in data:
                print("Number of items in 'data':", len(data['data']))
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(test())
