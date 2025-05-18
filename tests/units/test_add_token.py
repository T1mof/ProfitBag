import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bot.handlers.add_token import add_coin
from data.models import User, UserCoin


@pytest.mark.asyncio
async def test_add_new_coin():
    """Тестирование добавления новой монеты в портфель."""
    # Мок для сообщения пользователя
    message = AsyncMock()
    message.text = "/add BTC 0.5 50000"
    message.from_user.id = 12345

    # Мок для объекта пользователя
    user = User()
    user.user_id = 1
    user.telegram_id = 12345

    # Настройка моков для базы данных
    mock_session = AsyncMock()
    execute_result = MagicMock()
    mock_session.execute.return_value = execute_result

    # Настройка для поиска пользователя (найден)
    user_result = MagicMock()
    user_result.first.return_value = user

    # Настройка для поиска монеты (не найдена)
    coin_result = MagicMock()
    coin_result.first.return_value = None

    # Настройка последовательности результатов
    execute_result.scalars = MagicMock(side_effect=[user_result, coin_result])

    # Мокируем сессию базы данных
    context_manager = AsyncMock()
    context_manager.__aenter__.return_value = mock_session
    context_manager.__aexit__.return_value = None
    session_factory = MagicMock(return_value=context_manager)

    # Патчим доступ к базе данных
    with patch('bot.utils.db_pool.db.get_session', return_value=session_factory):
        with patch('bot.utils.db_pool.db.initialized', True):
            await add_coin(message)

    # Проверяем, что монета была добавлена
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    message.reply.assert_called_once()
    assert "Добавлено" in message.reply.call_args[0][0]
