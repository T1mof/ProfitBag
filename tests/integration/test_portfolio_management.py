"""
Интеграционное тестирование инвестиционного Telegram бота.
"""

import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Добавляем корневую директорию проекта в путь для импортов
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bot.handlers.add_token import add_coin
from bot.handlers.portfolio import show_portfolio
from bot.handlers.delete_token import delete_coin
from bot.utils.db_pool import db
from data.models import User, UserCoin


@pytest.fixture
def mock_db():
    """Создает мок базы данных для тестирования."""
    # Мокируем сессию и методы работы с БД
    session = AsyncMock()

    # Контекстный менеджер для асинхронной сессии
    async_context = AsyncMock()
    async_context.__aenter__ = AsyncMock(return_value=session)
    async_context.__aexit__ = AsyncMock(return_value=None)

    # Создаем мок-фабрику сессий
    session_factory = MagicMock(return_value=async_context)

    # Патчим доступ к базе данных
    with patch('bot.utils.db_pool.db.get_session', return_value=session_factory):
        db.initialized = True
        yield session


@pytest.fixture
def mock_crypto_price():
    """Мокирует API для получения цены криптовалют."""
    with patch('bot.utils.api_requests.fetch_crypto_price', AsyncMock(return_value=50000.0)):
        with patch('bot.handlers.portfolio.fetch_crypto_price', AsyncMock(return_value=50000.0)):
            yield 50000.0


@pytest.fixture
def create_telegram_message():
    """Создает мок сообщения Telegram."""
    def _create_message(text, user_id=12345):
        from aiogram import types

        # Создаем моки пользователя и сообщения
        user = MagicMock(spec=types.User)
        user.id = user_id

        message = MagicMock(spec=types.Message)
        message.from_user = user
        message.text = text

        # Моки для ответных методов
        message.answer = AsyncMock()
        message.reply = AsyncMock()

        return message

    return _create_message


@pytest.mark.asyncio
async def test_portfolio_workflow(mock_db, create_telegram_message, mock_crypto_price):
    """
    Тестирует сценарий:
    1. Пользователь добавляет монету в портфель
    2. Пользователь просматривает свой портфель
    3. Пользователь удаляет монету из портфеля
    """
    # Настройка аттрибутов тестовых данных
    user_id = 12345
    ticker = "BTC"
    amount = 0.5
    price = 45000.0

    # Настраиваем мок базы данных

    # 1. Создаем объекты для имитации результатов запросов
    user = User()
    user.user_id = 1
    user.telegram_id = user_id

    # Мокируем результаты execute
    execute_result = MagicMock()
    mock_db.execute = AsyncMock(return_value=execute_result)

    # Настраиваем для первого запроса (получение пользователя)
    user_result = MagicMock()
    user_result.first = MagicMock(return_value=user)
    execute_result.scalars = MagicMock(return_value=user_result)

    # Шаг 1: Добавляем монету
    add_msg = create_telegram_message(f"/add {ticker} {amount} {price}")
    await add_coin(add_msg)

    # Убедимся, что ответ содержит сообщение об успехе
    add_msg.reply.assert_called_once()

    # Шаг 2: Настраиваем моки для просмотра портфеля
    coin = UserCoin()
    coin.coin = ticker
    coin.amount = amount
    coin.purchase_price = price

    coins_result = MagicMock()
    coins_result.all = MagicMock(return_value=[coin])

    # Настраиваем последовательность вызовов для scalars
    execute_result.scalars = MagicMock(side_effect=[user_result, coins_result])

    # Создаем сообщение для портфеля
    portfolio_msg = create_telegram_message("/portfolio")

    # Мок для статусного сообщения, которое обновляется
    status_msg = AsyncMock()
    status_msg.edit_text = AsyncMock()
    portfolio_msg.answer.return_value = status_msg

    # Запрашиваем портфель
    await show_portfolio(portfolio_msg)

    # Проверяем результат
    status_msg.edit_text.assert_called_once()
    portfolio_text = status_msg.edit_text.call_args[0][0]

    # В тексте должны быть нужные данные
    assert ticker in portfolio_text, f"Тикер {ticker} не найден в ответе"
    assert "криптопортфель" in portfolio_text.lower() or "портфель" in portfolio_text.lower()

    # Шаг 3: Удаление монеты
    # Переопределяем последовательность вызовов для scalars
    coin_result = MagicMock()
    coin_result.first = MagicMock(return_value=coin)
    execute_result.scalars = MagicMock(side_effect=[user_result, coin_result])

    # Создаем сообщение для удаления
    delete_msg = create_telegram_message(f"/delete {ticker}")

    # Удаляем монету
    await delete_coin(delete_msg)

    # Проверяем ответ
    delete_msg.reply.assert_called_once()
    delete_text = delete_msg.reply.call_args[0][0]
    assert "удалена" in delete_text

    # Проверяем, что был вызван метод delete
    mock_db.delete.assert_called_once()
