from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    menu = State()
    add_product_name = State()
    add_product_price = State()
    add_product_category = State()
    edit_product_select = State()
    edit_product_name = State()
    edit_product_price = State()
    delete_product = State()
    new_category = State()
