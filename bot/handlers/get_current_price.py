import aiohttp
import ssl
import certifi
from aiogram import Router, types
from aiogram.filters import Command

get_current_price_router = Router()

async def fetch_crypto_price(symbol: str) -> float:
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

@get_current_price_router.message(Command("price"))
async def get_current_price(message: types.Message):
    parts = message.text.split()
    if len(parts) != 2:
        await message.reply("Неверный формат команды. Используйте: /price ТИКЕР\nПример: /price BTC")
        return
    ticker = parts[1].upper()
    try:
        price = await fetch_crypto_price(ticker)
        await message.reply(f"Текущая цена {ticker}: {price} USDT")
    except Exception as e:
        await message.reply(f"Ошибка: {e}")
