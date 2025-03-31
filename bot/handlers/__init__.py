from start import router as start_router
from portfolio import view_portfolio, portfolio_change
from add_token import add_coin
from delete_token import delete_coin
from edit_token import edit_coin
from get_old_price import get_old_price
from get_current_price import get_current_price

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
    dp.include_router(add_coin)
    dp.include_router(delete_coin)
    dp.include_router(edit_coin)
    dp.include_router(get_old_price)
    dp.include_router(get_current_price)
    dp.include_router(view_portfolio)
    dp.include_router(portfolio_change)
