import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from database.db import init_db
from handlers.user import menu, cart, checkout
from handlers.admin import products, settings
from config import API_TOKEN
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


dp.include_router(menu.router)
dp.include_router(cart.router)
dp.include_router(checkout.router)
dp.include_router(products.router)
dp.include_router(settings.router)


async def main():
    init_db()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
