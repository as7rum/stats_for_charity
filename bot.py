import asyncio
import logging
from aiogram import Bot, Dispatcher

from config.bot_config import API_TOKEN

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def send_message(id: str, message, parse_mode: str = None, reply_markup: str = None):
    await bot.send_message(id, message)