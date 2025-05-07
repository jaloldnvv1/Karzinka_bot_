from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_all_products


def get_admin_keyboard():
    buttons = [
        [InlineKeyboardButton(text="➕ Mahsulot qo'shish", callback_data="admin_add_product")],
        [InlineKeyboardButton(text="✏️ Mahsulotni tahrirlash", callback_data="admin_edit_product")],
        [InlineKeyboardButton(text="❌ Mahsulotni o'chirish", callback_data="admin_delete_product")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_all_products_keyboard(action):
    products = get_all_products()
    buttons = []

    for product_id, name, price in products:
        buttons.append([InlineKeyboardButton(
            text=f"{name} - {price:,} so'm",
            callback_data=f"{action}_{product_id}"
        )])

    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_category_selection_keyboard(categories, callback_prefix):
    buttons = []

    for category in categories:
        buttons.append([InlineKeyboardButton(text=category, callback_data=f"{callback_prefix}_{category}")])

    buttons.append([InlineKeyboardButton(text="➕ Yangi kategoriya", callback_data="add_new_category")])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
