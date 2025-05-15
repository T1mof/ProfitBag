import aiohttp
import ssl
import certifi
async def fetch_crypto_price(symbol: str) -> float:
    """
    Получает актуальную цену криптовалюты с Binance.
    symbol: например, 'BTC', 'ETH'
    Возвращает цену в USDT.
    """
    if not symbol.upper().endswith('USDT'):
        symbol = symbol.upper() + 'USDT'
    url = 'https://api.binance.com/api/v3/ticker/price'
    params = {'symbol': symbol}
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, ssl=ssl_context) as response:
            data = await response.json()
            if 'price' in data:
                return float(data['price'])
            else:
                raise ValueError(f"Не удалось получить цену для {symbol}")

async def test_fetch_binance_price():
    try:
        symbol = 'BTCUSDT'  # Пример тикера
        price = await fetch_crypto_price(symbol)
        print(f"Текущая цена {symbol}: {price} USDT")
    except Exception as e:
        print(f"Ошибка: {e}")