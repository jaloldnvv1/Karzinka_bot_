from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_categories, get_products_by_category, is_admin, get_cart


def get_main_keyboard(user_id):
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍 Mahsulotlar")],
        [KeyboardButton(text="🧺 Savatim")]
    ], resize_keyboard=True)

    if is_admin(user_id):
        keyboard.keyboard.append([KeyboardButton(text="👨‍💼 Admin panel")])

    return keyboard


def get_categories_keyboard():
    categories = get_categories()
    buttons = []

    for category in categories:
        buttons.append([InlineKeyboardButton(text=category, callback_data=f"category_{category}")])

    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_products_keyboard(category):
    products = get_products_by_category(category)
    buttons = []

    for product_id, name, price in products:
        buttons.append([InlineKeyboardButton(
            text=f"{name} - {price:,} so'm",
            callback_data=f"product_{product_id}"
        )])

    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_product_keyboard(product_id):
    buttons = [
        [
            InlineKeyboardButton(text="➕ Savatga qo'shish", callback_data=f"add_to_cart_{product_id}"),
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_products")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cart_keyboard(user_id):
    cart_items = get_cart(user_id)
    buttons = []

    for cart_id, _, _, _ in cart_items:
        buttons.append([InlineKeyboardButton(
            text=f"❌ #{cart_id} ni o'chirish",
            callback_data=f"remove_from_cart_{cart_id}"
        )])

    if cart_items:
        buttons.append([InlineKeyboardButton(text="💰 Hisob-kitob", callback_data="checkout")])

    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
