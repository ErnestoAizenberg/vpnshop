import os

from aiogram import Bot, Dispatcher, executor
from handlers import register_handlers

bot = Bot(token=os.getenv("BOT_TOKEN"))

dp = Dispatcher(bot)
register_handlers(dp)
executor.start_pulling(dp)
