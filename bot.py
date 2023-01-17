import asyncio
import logging
from aiogram import Bot, Dispatcher

from config.bot_config import API_TOKEN
from handlers import profile, start_command_and_profile_creation

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def send_message(id: str, message):
    await bot.send_message(id, message)


async def main():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp.include_router(start_command_and_profile_creation.router)
    dp.include_router(profile.router)

    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())