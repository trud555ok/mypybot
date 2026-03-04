import aiohttp

URL = "https://api.binance.com/api/v3/ticker/price?symbol=BONKUSDT"


async def get_price():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as resp:
            data = await resp.json()
            return float(data["price"])