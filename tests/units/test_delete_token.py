import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bot.handlers.delete_token import delete_coin
from data.models import User, UserCoin


@pytest.mark.asyncio
async def test_delete_entire_coin():
    """Проверка полного удаления монеты из портфеля."""
    # Мок для сообщения
    message = AsyncMock()
    message.text = "/delete BTC"
    message.from_user.id = 12345

    # Объекты для тестирования
    user = User()
    user.user_id = 1
    user.telegram_id = 12345

    coin = UserCoin()
    coin.user_id = 1
    coin.coin = "BTC"
    coin.amount = 0.5
    coin.purchase_price = 50000

    # Мокируем сессию базы данных
    mock_session = AsyncMock()
    execute_result = MagicMock()
    mock_session.execute.return_value = execute_result

    # Настраиваем последовательность результатов запросов
    user_result = MagicMock()
    user_result.first.return_value = user

    coin_result = MagicMock()
    coin_result.first.return_value = coin

    execute_result.scalars = MagicMock(side_effect=[user_result, coin_result])

    # Создаем контекстный менеджер для сессии
    context_manager = AsyncMock()
    context_manager.__aenter__.return_value = mock_session
    context_manager.__aexit__.return_value = None
    session_factory = MagicMock(return_value=context_manager)

    # Патчим доступ к БД
    with patch('bot.utils.db_pool.db.get_session', return_value=session_factory):
        with patch('bot.utils.db_pool.db.initialized', True):
            await delete_coin(message)

    # Проверяем результаты
    mock_session.delete.assert_called_once()
    mock_session.commit.assert_called_once()
    message.reply.assert_called_once()
    assert "удалена" in message.reply.call_args[0][0]
