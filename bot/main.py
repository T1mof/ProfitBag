import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, DATABASE_URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from bot.handlers import register_handlers  # функция для регистрации всех обработчиков команд
from bot.utils.api_requests import test_fetch_binance_price

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание асинхронного движка для подключения к базе данных
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание фабрики асинхронных сессий
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def main():
    # Инициализация хранилища состояний (можно использовать RedisStorage для продакшена)
    storage = MemoryStorage()

    # Инициализация бота
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")

    # Создание диспетчера с использованием хранилища состояний
    dp = Dispatcher(storage=storage)

    # Регистрация обработчиков (например, команды /start и /get_data)
    register_handlers(dp, AsyncSessionLocal)

    # Запуск поллинга (асинхронное получение обновлений от Telegram)
    try:
        logger.info("Бот запущен. Начало поллинга...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await engine.dispose()


if __name__ == '__main__':
    asyncio.run(test_fetch_binance_price()) #Это тест запросов к api binance
    asyncio.run(main())
