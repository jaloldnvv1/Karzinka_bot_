from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from states.user_states import UserStates
from database.db import get_cart, clear_cart

router = Router()

@router.callback_query(F.data == "checkout")
async def process_checkout(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    cart_items = get_cart(user_id)

    if not cart_items:
        await callback.answer(text="Savatingiz bo'sh!")
        return

    total = sum(quantity * price for _, _, quantity, price in cart_items)

    receipt = "🧾 Chek:\n\n"
    for _, name, quantity, price in cart_items:
        receipt += f"{name} x {quantity} = {quantity * price:,} so'm\n"

    receipt += f"\nUmumiy: {total:,} so'm\n"
    receipt += "\nXaridingiz uchun rahmat! 🙏"

    # Clear the cart
    clear_cart(user_id)

    await callback.answer()
    await callback.message.edit_text(
        receipt,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Bosh sahifa", callback_data="back_to_main")]
        ])
    )
    await state.set_state(UserStates.checkout)