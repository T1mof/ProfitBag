import aiohttp

async def fetch_binance_price(symbol: str) -> float:
    url = f'https://api.binance.com/api/v3/ticker/price'
    params = {'symbol': symbol.upper()}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
            if 'price' in data:
                return float(data['price'])
            else:
                raise ValueError(f"Не удалось получить цену для {symbol.upper()}. Ответ: {data}")
