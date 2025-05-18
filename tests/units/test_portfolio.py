import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bot.handlers.portfolio import show_portfolio
from data.models import User, UserCoin


@pytest.mark.asyncio
async def test_show_portfolio_with_coins():
    """Проверка отображения портфеля с монетами."""
    # Мок для сообщения
    message = AsyncMock()
    message.from_user.id = 12345

    # Создаем тестовые объекты
    user = User()
    user.user_id = 1
    user.telegram_id = 12345

    coins = [
        UserCoin(user_id=1, coin="BTC", amount=0.5, purchase_price=45000),
        UserCoin(user_id=1, coin="ETH", amount=2.0, purchase_price=3000)
    ]

    # Мокируем сессию БД
    mock_session = AsyncMock()
    execute_result = MagicMock()
    mock_session.execute.return_value = execute_result

    # Настраиваем последовательность результатов
    user_result = MagicMock()
    user_result.first.return_value = user

    coins_result = MagicMock()
    coins_result.all.return_value = coins

    execute_result.scalars = MagicMock(side_effect=[user_result, coins_result])

    # Мок для статусного сообщения
    status_msg = AsyncMock()
    status_msg.edit_text = AsyncMock()
    message.answer.return_value = status_msg

    # Создаем контекстный менеджер для сессии
    context_manager = AsyncMock()
    context_manager.__aenter__.return_value = mock_session
    context_manager.__aexit__.return_value = None
    session_factory = MagicMock(return_value=context_manager)

    # Патчим зависимости
    with patch('bot.utils.db_pool.db.get_session', return_value=session_factory):
        with patch('bot.utils.db_pool.db.initialized', True):
            with patch('bot.utils.api_requests.fetch_crypto_price', AsyncMock(side_effect=[50000, 3500])):
                with patch('bot.handlers.portfolio.fetch_crypto_price', AsyncMock(side_effect=[50000, 3500])):
                    await show_portfolio(message)

    # Проверяем результаты
    message.answer.assert_called_once()
    status_msg.edit_text.assert_called_once()
    portfolio_text = status_msg.edit_text.call_args[0][0]

    # Проверяем содержимое портфеля
    assert "BTC" in portfolio_text
    assert "ETH" in portfolio_text
    assert "45000" in portfolio_text  # Цена покупки BTC
    assert "50000" in portfolio_text  # Текущая цена BTC
