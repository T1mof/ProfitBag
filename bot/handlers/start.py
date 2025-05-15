from aiogram import Router, types
from aiogram.filters import Command
from bot.utils.keyboards import get_main_menu

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    # Отправляем приветственное сообщение с инлайн-кнопками
    await message.answer(
        f"Привет, {message.from_user.first_name}! Я бот для отслеживания криптовалютного портфеля.",
        reply_markup=get_main_menu()
    )

    # Также отправляем клавиатуру с командами
    await message.answer(
        "Используйте эти кнопки для быстрого доступа к командам:",
        reply_markup=get_main_menu()
    )


from aiogram.types import ReplyKeyboardRemove

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот для отслеживания криптовалютного портфеля.",
        reply_markup=ReplyKeyboardRemove()  # Удаляет старое меню
    )
    await message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu()        # Показывает новые инлайн-кнопки
    )
