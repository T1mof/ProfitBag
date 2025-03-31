from bot.handlers.start import router as start_router
from bot.handlers.portfolio import get_portfolio_router
from bot.handlers.add_token import add_coin_router
from bot.handlers.delete_token import delete_coin_router
from bot.handlers.edit_token import edit_token_router
from bot.handlers.get_old_price import get_old_price_router
from bot.handlers.get_current_price import get_current_price_router

# Глобальная переменная для пула соединений к БД
db_pool = None

def set_db_pool(pool):
    """
    Устанавливает пул соединений для использования в обработчике.
    """
    global db_pool
    db_pool = pool


def register_handlers(dp, pool):
    """
    Регистрирует все обработчики бота в диспетчере.

    Аргументы:
      dp   — объект Dispatcher из aiogram.
      pool — пул соединений к базе данных PostgreSQL.
    """
    # Передаём пул соединений в модуль с обработчиком запросов к API
    set_db_pool(pool)

    # Регистрируем роутеры
    dp.include_router(start_router)
    dp.include_router(add_coin_router)
    dp.include_router(delete_coin_router)
    dp.include_router(edit_token_router)
    dp.include_router(get_old_price_router)
    dp.include_router(get_current_price_router)
    dp.include_router(get_portfolio_router)