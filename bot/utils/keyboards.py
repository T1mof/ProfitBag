from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚀 Начать", callback_data="cmd_start"),
                InlineKeyboardButton(text="💼 Портфель", callback_data="cmd_portfolio")
            ],
            [
                InlineKeyboardButton(text="➕ Добавить", callback_data="cmd_add"),
                InlineKeyboardButton(text="✏️ Редактировать", callback_data="cmd_edit")
            ],
            [
                InlineKeyboardButton(text="💰 Узнать цену", callback_data="cmd_price"),
                InlineKeyboardButton(text="➖ Удалить", callback_data="cmd_delete")
            ]
        ]
    )

