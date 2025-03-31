import logging
from aiogram import Router, types
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from bot.utils.db import AsyncSessionLocal
from data.models import User, UserCoin
from aiogram.filters import Command

logger = logging.getLogger(__name__)
delete_coin_router = Router()


@delete_coin_router.message(Command("delete"))
async def delete_coin(message: types.Message):
    """
    Обработчик команды /delete <тикер>.
    Удаляет криптовалюту из портфеля пользователя.
    """
    # Разделение введённой команды на части
    try:
        _, ticker = message.text.split()
    except ValueError:
        await message.reply("Неверный формат команды. Используйте: /delete <тикер>")
        return

    telegram_id = str(message.from_user.id)

    async with AsyncSessionLocal() as session:
        try:
            # Проверка наличия пользователя в базе
            result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
            user = result.scalars().first()

            if not user:
                await message.reply("Пользователь не найден в базе данных.")
                return

            # Поиск монеты в портфеле пользователя
            user_coin = await session.execute(select(UserCoin).filter_by(user_id=user.user_id, coin=ticker.upper()))
            user_coin = user_coin.scalars().first()

            if not user_coin:
                await message.reply(f"Монета {ticker.upper()} не найдена в вашем портфеле.")
                return

            # Удаление монеты из портфеля
            await session.delete(user_coin)
            await session.commit()

            await message.reply(f"Монета {ticker.upper()} успешно удалена из вашего портфеля.")

        except SQLAlchemyError as e:
            await session.rollback()
            await message.reply("Произошла ошибка при удалении данных из базы.")
            print(f"Ошибка базы данных: {e}")