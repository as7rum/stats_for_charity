import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config.bot_config import API_TOKEN

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=API_TOKEN)
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(message.from_user.id)

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())