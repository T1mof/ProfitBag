import pytest
from unittest.mock import MagicMock
from bot.utils.db_pool import DatabasePool


def test_db_pool_initialization():
    """Проверка инициализации пула базы данных."""
    # Создаем экземпляр пула
    db_pool = DatabasePool()
    assert not db_pool.initialized
    assert db_pool.session_factory is None

    # Мок для фабрики сессий
    mock_factory = MagicMock()

    # Инициализируем пул
    db_pool.initialize(mock_factory)

    # Проверяем состояние после инициализации
    assert db_pool.initialized
    assert db_pool.session_factory is mock_factory


def test_get_session_before_initialization():
    """Проверка поведения при попытке получить сессию до инициализации."""
    db_pool = DatabasePool()
    assert db_pool.get_session() is None


def test_get_session_after_initialization():
    """Проверка получения сессии после инициализации."""
    db_pool = DatabasePool()
    mock_factory = MagicMock()

    db_pool.initialize(mock_factory)
    assert db_pool.get_session() is mock_factory
