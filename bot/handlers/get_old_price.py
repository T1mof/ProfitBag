import logging
from aiogram import Router, types
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from bot.utils.db import AsyncSessionLocal
from data.models import User, UserCoin

logger = logging.getLogger(__name__)
router = Router()


@router.message(commands=["get_price"])
async def get_old_price(message: types.Message):
    """
    Обработчик команды /get_price <тикер>.
    Отображает цену покупки указанной монеты в портфеле пользователя.
    """
    # Разделение введённой команды на части
    try:
        _, ticker = message.text.split()
    except ValueError:
        await message.reply("Неверный формат команды. Используйте: /get_price <тикер>")
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
            user_coin = await session.execute(
                select(UserCoin).filter_by(user_id=user.user_id, coin=ticker.upper())
            )
            user_coin = user_coin.scalars().first()

            if not user_coin:
                await message.reply(f"Монета {ticker.upper()} не найдена в вашем портфеле.")
                return

            # Отправка сообщения с ценой покупки монеты
            await message.reply(
                f"Цена покупки монеты {ticker.upper()}: {user_coin.purchase_price}"
            )

        except SQLAlchemyError as e:
            await message.reply("Произошла ошибка при получении данных из базы.")
            print(f"Ошибка базы данных: {e}")