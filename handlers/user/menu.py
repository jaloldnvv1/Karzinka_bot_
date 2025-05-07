from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from states.user_states import UserStates
from keyboards.user_kb import get_main_keyboard, get_categories_keyboard, get_products_keyboard
from database.db import get_product

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(UserStates.browsing)
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}!\n"
        f"Korzinka botiga xush kelibsiz. Mahsulotlarni ko'rish uchun tugmalardan foydalaning",
        reply_markup=get_main_keyboard(message.from_user.id)
    )


@router.message(F.text == "🛍 Mahsulotlar")
async def show_categories(message: Message, state: FSMContext):
    await state.set_state(UserStates.browsing)
    await message.answer(
        "Kategoriyani tanlang:",
        reply_markup=get_categories_keyboard()
    )


@router.callback_query(F.data.startswith("category_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split('_', 1)[1]

    await state.update_data(current_category=category)

    await callback.answer()
    await callback.message.edit_text(
        f"Kategoriya: {category}\nMahsulotni tanlang:",
        reply_markup=get_products_keyboard(category)
    )


@router.callback_query(F.data.startswith("product_"))
async def process_product(callback: CallbackQuery, state: FSMContext):
    from keyboards.user_kb import get_product_keyboard

    product_id = int(callback.data.split('_')[1])
    product = get_product(product_id)

    if not product:
        await callback.answer(text="Mahsulot topilmadi!")
        return

    product_id, name, price, category = product

    await state.update_data(current_product_id=product_id)

    await callback.answer()
    await callback.message.edit_text(
        f"📦 Mahsulot: {name}\n💰 Narxi: {price:,} so'm\n🏷 Kategoriya: {category}",
        reply_markup=get_product_keyboard(product_id)
    )


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(
        "Bosh sahifa",
        reply_markup=get_main_keyboard(callback.from_user.id)
    )
    await state.set_state(UserStates.browsing)


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "Kategoriyani tanlang:",
        reply_markup=get_categories_keyboard()
    )


@router.callback_query(F.data == "back_to_products")
async def back_to_products(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category = data.get('current_category')

    if not category:
        await back_to_categories(callback, state)
        return

    await callback.answer()
    await callback.message.edit_text(
        f"Kategoriya: {category}\nMahsulotni tanlang:",
        reply_markup=get_products_keyboard(category)
    )