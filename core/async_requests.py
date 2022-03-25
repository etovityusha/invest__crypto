import httpx


async def get_async(client: httpx.AsyncClient, url: str) -> dict:
    response = await client.get(url)
    return response.json()
