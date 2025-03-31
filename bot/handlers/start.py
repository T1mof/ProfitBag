from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    """
    Обработчик команды /start.
    Приветствует пользователя и сообщает о функционале бота.
    """
    await message.answer("Привет! Я бот для работы с внешним API и сохранения данных в PostgreSQL.")
