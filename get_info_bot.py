import asyncio
import logging
from contextlib import suppress
from random import randint
from typing import Optional

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Text
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from config.bot_config import API_TOKEN

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

user_data = {}
# ----------
# Это вариант с фабрикой колбэков

class JobTitleCallback(CallbackData, prefix="job_title_callbacks"):
    action: str
    value: Optional[str]


def get_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Стажер", callback_data=JobTitleCallback(action="change", value="Стажер"))
    builder.button(text="Лидер", callback_data=JobTitleCallback(action="change", value="Лидер"))
    builder.button(text="Тимлидер", callback_data=JobTitleCallback(action="change", value="Тимлидер"))
    builder.button(text="Ассистент", callback_data=JobTitleCallback(action="change", value="Ассистент"))
    builder.button(text="Подтвердить", callback_data=JobTitleCallback(action="finish"))
    builder.adjust(4)
    return builder.as_markup()


async def update_job_title(message: types.Message, new_value: str):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"Ваша позиция: {new_value}",
            reply_markup=get_keyboard()
        )


@dp.message(Command("job_title"))
async def cmd_job_title(message: types.Message):
    # user_data[message.from_user.id] = ''
    await message.answer("Ваша позиция: ", reply_markup=get_keyboard())


# Выбираем занимаемую позицию (должность)
@dp.callback_query(JobTitleCallback.filter(F.action == "change"))
async def callbacks_job_title_change(callback: types.CallbackQuery, callback_data: JobTitleCallback):
    # Текущее значение
    # user_value = user_data.get(callback.from_user.id, '')

    user_data[callback.from_user.id] = callback_data.value #user_value + callback_data.value
    await update_job_title(callback.message, callback_data.value)#user_value + callback_data.value)
    await callback.answer()


# Нажатие на кнопку "подтвердить"
@dp.callback_query(JobTitleCallback.filter(F.action == "finish"))
async def callbacks_job_title_finish(callback: types.CallbackQuery):
    # Текущее значение
    user_value = user_data.get(callback.from_user.id, '')

    await callback.message.edit_text(f"Занимаемая вами позиция: {user_value}")
    await callback.answer()


# Запуск бота
async def main():
    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())