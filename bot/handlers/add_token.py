import logging
from aiogram import Router, types
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from bot.utils.db import AsyncSessionLocal
from data.models import User, UserCoin
from aiogram.filters import Command

logger = logging.getLogger(__name__)
add_coin_router = Router()


@add_coin_router.message(Command("add"))
async def add_coin(message: types.Message):
    """
    Обработчик команды /add <тикер> <кол-во> <цена_покупки>.
    Добавляет криптовалюту в портфель пользователя.
    """
    # Разделение введённой команды на части
    try:
        _, ticker, amount, purchase_price = message.text.split()
        amount = float(amount)
        purchase_price = float(purchase_price)
    except ValueError:
        await message.reply("Неверный формат команды. Используйте: /add <тикер> <кол-во> <цена_покупки>")
        return

    telegram_id = str(message.from_user.id)

    async with AsyncSessionLocal() as session:
        try:
            # Проверка наличия пользователя в базе
            result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
            user = result.scalars().first()

            if not user:
                # Создание нового пользователя, если его нет в базе
                user = User(telegram_id=telegram_id)
                session.add(user)
                await session.commit()

            # Добавление новой записи о криптовалюте в портфель пользователя
            user_coin = UserCoin(user_id=user.user_id, coin=ticker.upper(), amount=amount, purchase_price=purchase_price)
            session.add(user_coin)
            await session.commit()

            await message.reply(f"Добавлено {amount} {ticker.upper()} по цене {purchase_price} в ваш портфель.")

        except SQLAlchemyError as e:
            await session.rollback()
            await message.reply("Произошла ошибка при добавлении данных в базу.")
            print(f"Ошибка базы данных: {e}")