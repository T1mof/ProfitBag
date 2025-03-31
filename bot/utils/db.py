import logging
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import DATABASE_URL  # Убедитесь, что этот параметр определён в вашем конфигурационном файле

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

# Базовый класс для моделей SQLAlchemy
class Base(AsyncAttrs, DeclarativeBase):
    pass

# Функция для инициализации подключения к базе данных
async def init_db():
    async with engine.begin() as conn:
        # Импортируйте здесь все модули с моделями, чтобы они были зарегистрированы перед созданием таблиц
        # Например: from . import models
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы успешно созданы.")

# Функция для закрытия подключения к базе данных
async def close_db():
    await engine.dispose()
    logger.info("Подключение к базе данных закрыто.")
