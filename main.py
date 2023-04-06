import asyncio
import logging

from bot import bot, dp
from handlers import (start_command_and_profile_creation, profile, change_profile, deals, statistics_options, team)

async def main():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp.include_router(start_command_and_profile_creation.router)
    dp.include_router(profile.router)
    dp.include_router(change_profile.router)
    dp.include_router(statistics_options.router)
    dp.include_router(deals.router)
    dp.include_router(team.router)

    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())