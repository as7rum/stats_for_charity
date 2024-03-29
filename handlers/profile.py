from aiogram import Router, types, F
from aiogram.filters.text import Text
from aiogram.filters.command import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.exceptions import TelegramBadRequest
from aiogram import html
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

import pprint
from contextlib import suppress
from typing import Optional

from google_sheets_services.person_sheets_service import PersonSheetsService
from models.person import Person
from models.valid import age
from bot import bot

router = Router()  # [1]


def person_current_profile(person: Person()):
    
    service = PersonSheetsService()
    try:
        chief = service.get_person_by_username(person.chief)

        if chief.name:
            return f'''Вот так твой профиль выглядит сейчас✨

Всем, привет! Меня зовут <b>{person.name}</b>.
<i>Занимаемая позиция</i>: <b>{person.job_title}</b>
<i>Возраст</i>: <b>{age(person.birthdate)}</b>
<i>Наставник</i>: <b>{chief.name}</b>
<i>Немного обо мне</i>:
<b>{person.description}</b>'''
    except:
        return f'''Вот так твой профиль выглядит сейчас✨

Всем, привет! Меня зовут <b>{person.name}</b>.
<i>Занимаемая позиция</i>: <b>{person.job_title}</b>
<i>Возраст</i>: <b>{age(person.birthdate)}</b>
<i>Наставник</i>: <b>{'None' if person.chief == None else person.chief.username}</b>
<i>Немного обо мне</i>:
<b>{person.description}</b>'''


class ProfileCallback(CallbackData, prefix="profile_callbacks"):
    action: str
    # value: Optional[str]

def get_profile_keyboard():
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

async def update_profile_page(message: types.Message, new_text: str, keyboard_builder):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            new_text,
            reply_markup=keyboard_builder)

def change_profile_keyboard():
        builder = InlineKeyboardBuilder()
        builder.button(text="Изменить имя", callback_data=ProfileCallback(action="change_name"))
        builder.button(text="Изменить должность", callback_data=ProfileCallback(action="change_job_title"))
        builder.button(text="Изменить дату рождения", callback_data=ProfileCallback(action="change_birthdate"))
        builder.button(text="Изменить описание", callback_data=ProfileCallback(action="change_description"))
        builder.button(text="Назад", callback_data=ProfileCallback(action="back"))
        builder.adjust(2)
        return builder.as_markup()

async def send_profile_page(username: str, chat_id: str|int):
    person_profile = profile(username)
    await bot.send_message(chat_id, person_profile,
    parse_mode='HTML', reply_markup=get_profile_keyboard())

@router.callback_query(ProfileCallback.filter(F.action == "change_profile"))
async def callbacks_change_profile(callback: types.CallbackQuery, callback_data: ProfileCallback):
    global person_profile
    
    if person_profile:
        await callback.message.edit_text(person_profile, parse_mode='HTML', 
        reply_markup=change_profile_keyboard())
        await callback.answer(text="Переходим в настройки профиля.")
        return
    person_profile = profile(callback.from_user.username)
    await callback.message.edit_text(person_profile, parse_mode='HTML', 
        reply_markup=change_profile_keyboard())
    await callback.answer(text="Переходим в настройки профиля.")

@router.callback_query(ProfileCallback.filter(F.action == "back"))
async def callbacks_back_command(callback: types.CallbackQuery, callback_data: ProfileCallback, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(person_profile, parse_mode='HTML', reply_markup=get_profile_keyboard())
    await callback.answer(text="Возвращаемся назад.")

