import asyncio
import logging
from contextlib import suppress
from random import randint
from typing import Optional

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.bot_config import API_TOKEN
from google_sheets_services.person_sheets_service import PersonSheetsService
from models.valid import age

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

class ProfileCallback(CallbackData, prefix="profile_callbacks"):
    action: str
    # value: Optional[str]

def get_keyboard():
        builder = InlineKeyboardBuilder()
        builder.button(text="Изменить профиль", callback_data=ProfileCallback(action="change_profile"))#, value="Изменить профиль"))
        builder.button(text="Статистика", callback_data=ProfileCallback(action="statistics"))#, value="Статистика"))
        builder.button(text="Сделки", callback_data=ProfileCallback(action="deals"))#, value="Сделки"))
        builder.button(text="Команда", callback_data=ProfileCallback(action="team"))#, value="Команда"))
        builder.adjust(2)
        return builder.as_markup()

def profile(username: str):
    global person_profile

    service = PersonSheetsService()
    person = service.get_person_by_username(username)
    person_chief = service.get_person_by_username(person.chief)
    person_profile = f'''
Всем, привет! Меня зовут <b>{person.name}</b>.
<i>Занимаемая позиция</i>: <b>{person.job_title}</b>
<i>Возраст</i>: <b>{age(person.birthdate)}</b>
<i>Наставник</i>: <b>{person_chief.name}</b>
<i>Немного обо мне</i>:
<b>{person.description}</b>'''
    return person_profile

async def update_profile(message: types.Message, new_text: str):
    with suppress(TelegramBadRequest):
        
        builder = InlineKeyboardBuilder()
        builder.button(text="Назад", callback_data=ProfileCallback(action="back"))

        await message.edit_text(
            new_text,
            reply_markup=builder.as_markup()
        )

async def send_profile(username, chat_id):
    person_profile = profile(username)
    await bot.send_message(chat_id, person_profile, parse_mode="HTML", reply_markup=get_keyboard())

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await send_profile(message.from_user.username, message.from_user.id)
    # profile(message.from_user.username)
    # await bot.send_message(message.from_user.id, person_profile,
    #  parse_mode="HTML", reply_markup=get_keyboard())

@dp.callback_query(ProfileCallback.filter(F.action == "change_profile"))
async def callbacks_change_profile(callback: types.CallbackQuery, callback_data: ProfileCallback):
    await update_profile(callback.message, 'Здесь должны быть функции для изменения профиля')
    await callback.answer(text="Переходим в настройки профиля.")

@dp.callback_query(ProfileCallback.filter(F.action == "statistics"))
async def callbacks_statistics(callback: types.CallbackQuery, callback_data: ProfileCallback):
    await update_profile(callback.message, 'Здесь должна быть статистика')
    await callback.answer(text="Открываем статистику.")

@dp.callback_query(ProfileCallback.filter(F.action == "deals"))
async def callbacks_deals(callback: types.CallbackQuery, callback_data: ProfileCallback):
    await update_profile(callback.message, 'Здесь должны быть сделки')
    await callback.answer(text="Открываем сделки.")

@dp.callback_query(ProfileCallback.filter(F.action == "team"))
async def callbacks_team(callback: types.CallbackQuery, callback_data: ProfileCallback):
    await update_profile(callback.message, 'Здесь должен быть список членов команды')
    await callback.answer(text="Загружаем всех членов команды.")

@dp.callback_query(ProfileCallback.filter(F.action == "back"))
async def callbacks_back_com(callback: types.CallbackQuery, callback_data: ProfileCallback):
    await callback.message.edit_text(person_profile, parse_mode='HTML', reply_markup=get_keyboard())
    await callback.answer(text="Эта функция пока не доступна.")



# Запуск бота
async def main():
    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())