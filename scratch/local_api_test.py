import asyncio
import httpx

async def test():
    try:
        async with httpx.AsyncClient() as c:
            res = await c.get('http://127.0.0.1:8000/companies/')
            print("LOCAL API STATUS:", res.status_code)
            print("LOCAL API DATA:", res.text[:200])
    except Exception as e:
        print("Error connecting to local API:", e)

if __name__ == "__main__":
    asyncio.run(test())
