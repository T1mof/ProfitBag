import logging
from aiogram import Router, types
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from bot.utils.db import AsyncSessionLocal
from data.models import User, UserCoin
from bot.utils.api_requests import fetch_binance_price

logger = logging.getLogger(__name__)
router = Router()

@router.message(commands=["portfolio"])
async def view_portfolio(message: types.Message):
    """
    Обработчик команды /portfolio.
    Отображает все монеты в портфеле пользователя с их тикерами, количеством и ценами покупки.
    """
    telegram_id = str(message.from_user.id)

    async with AsyncSessionLocal() as session:
        try:
            # Проверка наличия пользователя в базе
            result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
            user = result.scalars().first()

            if not user:
                await message.reply("Пользователь не найден в базе данных.")
                return

            # Получение всех монет пользователя
            user_coins = await session.execute(
                select(UserCoin).filter_by(user_id=user.user_id)
            )
            user_coins = user_coins.scalars().all()

            if not user_coins:
                await message.reply("Ваш портфель пуст.")
                return

            # Формирование сообщения с данными о монетах
            portfolio_message = "Ваш портфель:\n"
            for user_coin in user_coins:
                portfolio_message += (
                    f"Тикер: {user_coin.coin}, "
                    f"Количество: {user_coin.amount}, "
                    f"Цена покупки: {user_coin.purchase_price}\n"
                )

            await message.reply(portfolio_message)

        except SQLAlchemyError as e:
            await message.reply("Произошла ошибка при получении данных из базы.")
            print(f"Ошибка базы данных: {e}")



@router.message(commands=["portfolio_change"])
async def portfolio_change(message: types.Message):
    """
    Обработчик команды /portfolio_change.
    Вычисляет процентное и абсолютное изменение стоимости портфеля пользователя.
    """
    telegram_id = str(message.from_user.id)
    total_initial_value = 0
    total_current_value = 0

    async with AsyncSessionLocal() as session:
        try:
            # Получение пользователя из базы данных
            result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
            user = result.scalars().first()

            if not user:
                await message.reply("Пользователь не найден в базе данных.")
                return

            # Получение всех монет пользователя
            result = await session.execute(select(UserCoin).filter_by(user_id=user.user_id))
            user_coins = result.scalars().all()

            if not user_coins:
                await message.reply("Ваш портфель пуст.")
                return

            # Вычисление общего изменения стоимости портфеля
            for user_coin in user_coins:
                try:
                    current_price = await fetch_binance_price(user_coin.coin)
                    initial_value = user_coin.amount * user_coin.purchase_price
                    current_value = user_coin.amount * current_price
                    total_initial_value += initial_value
                    total_current_value += current_value
                except ValueError as e:
                    await message.reply(str(e))
                    return

            # Вычисление процентного и абсолютного изменения
            if total_initial_value > 0:
                change_percentage = ((total_current_value - total_initial_value) / total_initial_value) * 100
                change_amount = total_current_value - total_initial_value
                await message.reply(
                    f"Общая стоимость вашего портфеля:\n"
                    f"Начальная стоимость: {total_initial_value:.2f} USD\n"
                    f"Текущая стоимость: {total_current_value:.2f} USD\n"
                    f"Изменение стоимости портфеля: {change_amount:.2f} USD ({change_percentage:+.2f}%)"
                )
            else:
                await message.reply("Невозможно вычислить изменение стоимости портфеля: начальная стоимость равна нулю.")

        except Exception as e:
            await message.reply("Произошла ошибка при обработке запроса.")
            print(f"Ошибка: {e}")