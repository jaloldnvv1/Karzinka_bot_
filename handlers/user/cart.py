from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from states.user_states import UserStates
from keyboards.user_kb import get_main_keyboard, get_cart_keyboard, get_product_keyboard
from database.db import get_cart, add_to_cart, remove_from_cart, get_product

router = Router()

@router.message(F.text == "🧺 Savatim")
async def show_cart(message: Message, state: FSMContext):
    user_id = message.from_user.id
    cart_items = get_cart(user_id)

    if not cart_items:
        await message.answer("Savatingiz bo'sh!", reply_markup=get_main_keyboard(user_id))
        await state.set_state(UserStates.browsing)
        return

    total = sum(quantity * price for _, _, quantity, price in cart_items)

    cart_text = "🧺 Savatingizdagi mahsulotlar:\n\n"
    for cart_id, name, quantity, price in cart_items:
        cart_text += f"#{cart_id} {name} x {quantity} = {quantity * price:,} so'm\n"

    cart_text += f"\nUmumiy: {total:,} so'm"

    await message.answer(
        cart_text,
        reply_markup=get_cart_keyboard(user_id)
    )
    await state.set_state(UserStates.viewing_cart)

@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_product_to_cart(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split('_')[-1])
    user_id = callback.from_user.id

    add_to_cart(user_id, product_id)
    product = get_product(product_id)

    await callback.answer(
        text=f"{product[1]} savatga qo'shildi!",
        show_alert=True
    )

    # Return to product view
    await callback.message.edit_text(
        f"📦 Mahsulot: {product[1]}\n💰 Narxi: {product[2]:,} so'm\n🏷 Kategoriya: {product[3]}\n\n✅ Savatga qo'shildi!",
        reply_markup=get_product_keyboard(product_id)
    )

@router.callback_query(F.data.startswith("remove_from_cart_"))
async def remove_product_from_cart(callback: CallbackQuery, state: FSMContext):
    cart_id = int(callback.data.split('_')[-1])
    user_id = callback.from_user.id

    remove_from_cart(user_id, cart_id)

    await callback.answer(
        text="Mahsulot savatdan olib tashlandi!",
        show_alert=True
    )

    # Update cart view
    cart_items = get_cart(user_id)

    if not cart_items:
        await callback.message.edit_text(
            "Savatingiz bo'sh!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")]
            ])
        )
        return

    total = sum(quantity * price for _, _, quantity, price in cart_items)

    cart_text = "🧺 Savatingizdagi mahsulotlar:\n\n"
    for cart_id, name, quantity, price in cart_items:
        cart_text += f"#{cart_id} {name} x {quantity} = {quantity * price:,} so'm\n"

    cart_text += f"\nUmumiy: {total:,} so'm"

    await callback.message.edit_text(
        cart_text,
        reply_markup=get_cart_keyboard(user_id))