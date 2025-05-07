from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    browsing = State()
    viewing_product = State()
    viewing_cart = State()
    checkout = State()
