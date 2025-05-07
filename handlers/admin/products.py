from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from states.admin_states import AdminStates
from keyboards.admin_kb import get_admin_keyboard, get_all_products_keyboard, get_category_selection_keyboard
from keyboards.user_kb import get_main_keyboard
from database.db import is_admin, get_product, get_categories, add_product, update_product_name, update_product_price, \
    delete_product

router = Router()


@router.message(F.text == "👨‍💼 Admin panel")
async def admin_panel(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if not is_admin(user_id):
        await message.answer("Sizda admin huquqlari yo'q!")
        return

    await message.answer(
        "Admin panel. Amalni tanlang:",
        reply_markup=get_admin_keyboard()
    )
    await state.set_state(AdminStates.menu)


@router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "Admin panel. Amalni tanlang:",
        reply_markup=get_admin_keyboard()
    )
    await state.set_state(AdminStates.menu)


@router.callback_query(F.data == "admin_add_product")
async def admin_add_product(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "Yangi mahsulot qo'shish.\nMahsulot nomini kiriting:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
        ])
    )
    await state.set_state(AdminStates.add_product_name)


@router.message(AdminStates.add_product_name)
async def process_product_name(message: Message, state: FSMContext):
    await state.update_data(product_name=message.text)

    await message.answer(
        "Mahsulot narxini kiriting (faqat raqam):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
        ])
    )
    await state.set_state(AdminStates.add_product_price)


@router.message(AdminStates.add_product_price)
async def process_product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(product_price=price)

        # Get categories for selection
        categories = get_categories()

        await message.answer(
            "Mahsulot kategoriyasini tanlang yoki yangi kategoriya qo'shing:",
            reply_markup=get_category_selection_keyboard(categories, "add_cat")
        )
        await state.set_state(AdminStates.add_product_category)

    except ValueError:
        await message.answer("Iltimos, faqat raqam kiriting!")


@router.callback_query(F.data.startswith("add_cat_"))
async def process_product_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split('_', 2)[2]
    await state.update_data(product_category=category)

    data = await state.get_data()
    name = data['product_name']
    price = data['product_price']

    add_product(name, price, category)

    await callback.answer()
    await callback.message.edit_text(
        f"✅ Mahsulot qo'shildi!\n\nNomi: {name}\nNarxi: {price:,} so'm\nKategoriya: {category}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Admin panelga qaytish", callback_data="back_to_admin")]
        ])
    )
    await state.set_state(AdminStates.menu)


@router.callback_query(F.data == "add_new_category")
async def add_new_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "Yangi kategoriya nomini kiriting:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
        ])
    )
    await state.set_state(AdminStates.new_category)


@router.message(AdminStates.new_category)
async def process_new_category(message: Message, state: FSMContext):
    new_category = message.text
    await state.update_data(product_category=new_category)

    data = await state.get_data()
    name = data['product_name']
    price = data['product_price']

    add_product(name, price, new_category)

    await message.answer(
        f"✅ Mahsulot qo'shildi!\n\nNomi: {name}\nNarxi: {price:,} so'm\nKategoriya: {new_category}",
        reply_markup=get_main_keyboard(message.from_user.id)
    )
    await state.set_state(AdminStates.menu)


@router.callback_query(F.data == "admin_edit_product")
async def admin_edit_product(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "Tahrirlash uchun mahsulotni tanlang:",
        reply_markup=get_all_products_keyboard("edit")
    )
    await state.set_state(AdminStates.edit_product_select)


@router.callback_query(F.data.startswith("edit_"))
async def select_product_to_edit(callback: CallbackQuery, state: FSMContext):
    if len(callback.data.split('_')) == 2:
        product_id = int(callback.data.split('_')[1])
        product = get_product(product_id)

        if not product:
            await callback.answer(text="Mahsulot topilmadi!")
            return

        await state.update_data(edit_product_id=product_id)

        buttons = [
            [InlineKeyboardButton(text="✏️ Nomini o'zgartirish", callback_data="edit_name")],
            [InlineKeyboardButton(text="💰 Narxini o'zgartirish", callback_data="edit_price")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
        ]

        await callback.answer()
        await callback.message.edit_text(
            f"Mahsulot: {product[1]}\nNarxi: {product[2]:,} so'm\nKategoriya: {product[3]}\n\nNima o'zgartirmoqchisiz?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
    elif callback.data == "edit_name":
        await callback.answer()
        await callback.message.edit_text(
            "Yangi nomni kiriting:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
            ])
        )
        await state.set_state(AdminStates.edit_product_name)
    elif callback.data == "edit_price":
        await callback.answer()
        await callback.message.edit_text(
            "Yangi narxni kiriting (faqat raqam):",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
            ])
        )
        await state.set_state(AdminStates.edit_product_price)


@router.message(AdminStates.edit_product_name)
async def process_edit_name(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data['edit_product_id']
    new_name = message.text

    update_product_name(product_id, new_name)

    await message.answer(
        f"✅ Mahsulot nomi o'zgartirildi: {new_name}",
        reply_markup=get_main_keyboard(message.from_user.id)
    )
    await state.set_state(AdminStates.menu)
    await state.set_state(AdminStates.menu)


@router.message(AdminStates.edit_product_price)
async def process_edit_price(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        product_id = data['edit_product_id']
        new_price = float(message.text)

        update_product_price(product_id, new_price)

        await message.answer(
            f"✅ Mahsulot narxi o'zgartirildi: {new_price:,} so'm",
            reply_markup=get_main_keyboard(message.from_user.id)
        )
        await state.set_state(AdminStates.menu)
    except ValueError:
        await message.answer("Iltimos, faqat raqam kiriting!")


@router.callback_query(F.data == "admin_delete_product")
async def admin_delete_product(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "O'chirish uchun mahsulotni tanlang:",
        reply_markup=get_all_products_keyboard("delete")
    )
    await state.set_state(AdminStates.delete_product)


@router.callback_query(F.data.startswith("delete_"))
async def delete_product_handler(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split('_')[1])
    product = get_product(product_id)

    if not product:
        await callback.answer(text="Mahsulot topilmadi!")
        return

    delete_product(product_id)

    await callback.answer()
    await callback.message.edit_text(
        f"✅ Mahsulot o'chirildi: {product[1]}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Admin panelga qaytish", callback_data="back_to_admin")]
        ])
    )
    await state.set_state(AdminStates.menu)