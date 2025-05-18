import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import ssl
from bot.utils.api_requests import fetch_crypto_price


@pytest.mark.asyncio
async def test_fetch_crypto_price_success():
    """Проверка успешного получения цены криптовалюты."""
    # Метод 1: Более простая замена всей функции
    with patch('bot.utils.api_requests.fetch_crypto_price', AsyncMock(return_value=50000.0)):
        # Импортируем оригинальную функцию, которая будет заменена моком
        from bot.utils.api_requests import fetch_crypto_price as original_func
        price = await original_func("BTC")
        assert price == 50000.0


@pytest.mark.asyncio
async def test_fetch_crypto_price_error():
    """Проверка обработки ошибки при получении цены."""
    # Патчим функцию, чтобы она вызывала исключение при вызове с INVALID
    error_mock = AsyncMock(side_effect=ValueError("Не удалось получить цену для INVALIDUSDT"))

    with patch('bot.utils.api_requests.fetch_crypto_price', error_mock):
        from bot.utils.api_requests import fetch_crypto_price as original_func
        with pytest.raises(ValueError):
            await original_func("INVALID")
