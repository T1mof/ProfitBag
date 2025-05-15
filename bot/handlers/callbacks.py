from aiogram import Router, types, F

router = Router()

@router.callback_query(F.data == "cmd_start")
async def start_callback(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Бот уже запущен! Используйте меню для дальнейших действий.")

@router.callback_query(F.data == "cmd_portfolio")
async def portfolio_callback(callback: types.CallbackQuery):
    await callback.answer()
    # Здесь вызовите ваш show_portfolio
    from bot.handlers.portfolio import show_portfolio
    await show_portfolio(callback.message)

@router.callback_query(F.data == "cmd_add")
async def add_callback(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Для добавления используйте команду:\n/add ТИКЕР КОЛИЧЕСТВО ЦЕНА\nнапример: /add BTC 0.1 45000")

@router.callback_query(F.data == "cmd_edit")
async def edit_callback(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Для редактирования используйте команду:\n/edit ТИКЕР КОЛИЧЕСТВО ЦЕНА\nнапример: /edit BTC 0.2 50000")

@router.callback_query(F.data == "cmd_price")
async def price_callback(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Введите команду:\n/price ТИКЕР\nнапример: /price BTC")

@router.callback_query(F.data == "cmd_delete")
async def delete_callback(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Для удаления используйте команду:\n/delete ТИКЕР [КОЛИЧЕСТВО]\nнапример: /delete BTC или /delete BTC 0.05")
