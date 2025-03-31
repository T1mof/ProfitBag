import logging
from aiogram import Router, types
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from bot.utils.db import AsyncSessionLocal
from data.models import User, UserCoin

logger = logging.getLogger(__name__)
router = Router()


@router.message(commands=["edit"])
async def edit_coin(message: types.Message):
    """
    Обработчик команды /edit <тикер> <новое_количество> <новая_цена_покупки>.
    Редактирует криптовалюту в портфеле пользователя.
    """
    # Разделение введённой команды на части
    try:
        _, ticker, new_amount, new_purchase_price = message.text.split()
        new_amount = float(new_amount)
        new_purchase_price = float(new_purchase_price)
    except ValueError:
        await message.reply(
            "Неверный формат команды. Используйте: /edit <тикер> <новое_количество> <новая_цена_покупки>")
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

            # Обновление данных о монете в портфеле
            user_coin.amount = new_amount
            user_coin.purchase_price = new_purchase_price
            await session.commit()

            await message.reply(
                f"Монета {ticker.upper()} успешно обновлена: {new_amount} по цене {new_purchase_price}.")

        except SQLAlchemyError as e:
            await session.rollback()
            await message.reply("Произошла ошибка при обновлении данных в базе.")
            print(f"Ошибка базы данных: {e}")