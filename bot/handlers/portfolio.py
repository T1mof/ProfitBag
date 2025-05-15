from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.future import select
import logging
from data.models import User, UserCoin, PortfolioHistory
from bot.utils.db_pool import db
from bot.utils.api_requests import fetch_crypto_price

get_portfolio_router = Router()
logger = logging.getLogger(__name__)


@get_portfolio_router.message(Command("portfolio"))
async def show_portfolio(message: types.Message):
    status_msg = await message.answer("Запрашиваю данные о вашем портфеле...")
    try:
        telegram_id = int(message.from_user.id)
        session_factory = db.get_session()
        async with session_factory() as session:
            result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
            user = result.scalars().first()
            if not user:
                await status_msg.edit_text("У вас пока нет портфеля. Используйте /add для добавления криптовалюты.")
                return
            coins_result = await session.execute(select(UserCoin).filter_by(user_id=user.user_id))
            user_coins = list(coins_result.scalars().all())
            if not user_coins:
                await status_msg.edit_text("Ваш портфель пуст. Используйте /add для добавления криптовалюты.")
                return

            portfolio_text = "📊 <b>Ваш криптопортфель:</b>\n\n"
            total_value = 0
            total_actual = 0

            for coin in user_coins:
                ticker = coin.coin.upper()
                amount = float(coin.amount)
                purchase_price = float(coin.purchase_price)
                value = amount * purchase_price
                total_value += value

                try:
                    actual_price = await fetch_crypto_price(ticker)
                    actual_value = amount * actual_price
                    total_actual += actual_value
                    actual_price_str = f"{actual_price:.2f} USDT"
                    actual_value_str = f"{actual_value:.2f} USDT"
                except Exception:
                    actual_price_str = "н/д"
                    actual_value_str = "н/д"

                portfolio_text += (
                    f"🪙 <b>{ticker}</b>: {amount} монет\n"
                    f"   💰 Цена покупки: {purchase_price} USDT\n"
                    f"   🌐 Актуальная цена: {actual_price_str}\n"
                    f"   💵 Текущая стоимость: {actual_value_str}\n\n"
                )

            portfolio_text += (
                f"<b>Общая стоимость портфеля (по ценам покупки):</b> {total_value:.2f} USDT\n"
                f"<b>Общая стоимость портфеля (по актуальным ценам):</b> {total_actual:.2f} USDT"
            )

            await status_msg.edit_text(portfolio_text)
    except Exception as e:
        await status_msg.edit_text(f"Ошибка при получении портфеля: {e}")



@get_portfolio_router.callback_query(lambda c: c.data == "portfolio_change")
async def show_portfolio_history(callback: types.CallbackQuery):
    """
    Обработчик кнопки "Динамика портфеля".
    Показывает историю изменения стоимости портфеля.
    """
    await callback.answer()
    status_msg = await callback.message.answer("Запрашиваю данные об изменении вашего портфеля...")

    try:
        telegram_id = int(callback.from_user.id)

        session_factory = db.get_session()
        if session_factory is None:
            await status_msg.edit_text("⚠️ Ошибка: соединение с базой данных не установлено.")
            return

        async with session_factory() as session:
            # Находим пользователя
            user_result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
            user = user_result.scalars().first()

            if not user:
                await status_msg.edit_text("Пользователь не найден в базе данных.")
                return

            # Получаем историю портфеля
            history_result = await session.execute(
                select(PortfolioHistory)
                .filter_by(user_id=user.user_id)
                .order_by(PortfolioHistory.timestamp.desc())
                .limit(20)
            )
            history = list(history_result.scalars().all())

            if not history:
                await status_msg.edit_text(
                    "Данные о динамике портфеля отсутствуют. Добавьте или удалите монеты для начала отслеживания."
                )
                return

            # Формируем текстовый отчет
            text = "📈 <b>Динамика стоимости портфеля:</b>\n\n"

            # Выводим последние 10 записей в обратном порядке (от старых к новым)
            for record in list(reversed(history))[:10]:
                date_str = record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                text += f"{date_str}: {float(record.total_value):.2f} USDT\n"

            # Находим изменение за последние сутки
            if len(history) >= 2:
                latest_value = float(history[0].total_value)
                oldest_value = float(history[-1].total_value)
                percent_change = ((latest_value - oldest_value) / oldest_value) * 100 if oldest_value > 0 else 0

                text += f"\n<b>Общее изменение:</b> {percent_change:.2f}%"

                if percent_change > 0:
                    text += " 📈"
                elif percent_change < 0:
                    text += " 📉"

            await status_msg.edit_text(text)

    except Exception as e:
        logger.error(f"Ошибка при отображении динамики портфеля: {e}", exc_info=True)
        await status_msg.edit_text(
            f"⚠️ Произошла ошибка при получении данных динамики портфеля.\n"
            f"Тип ошибки: {type(e).__name__}\n"
            f"Попробуйте позже или обратитесь к администратору."
        )
