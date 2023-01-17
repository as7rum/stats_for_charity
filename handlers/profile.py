from aiogram import Router
from aiogram.filters.text import Text
from aiogram.filters.command import Command
from aiogram.types import Message, ReplyKeyboardRemove
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
from config.messages import START_COMMAND_MESSAGE

router = Router()  # [1]

@router.message(Text(text="профиль", ignore_case=True))
async def send_profile(message: Message):
    person_data = PersonSheetsService()
    person = person_data.get_person(message.from_user.id)
    pprint.pprint (person)
    profile_message = f'''
Имя: {person.name} ({person.job_title})
Дата рождения: {person.birthdate}
Лидер: {person.chief}
Описание: {person.description}
    '''
    await message.answer(profile_message)

def person_current_profile(person: Person()):
    
    service = PersonSheetsService()
    try:
        chief = service.get_person_by_username(person.chief)

        if chief.name:
            return f'''Вот так твой профиль выглядит сейчас✨

Привет, меня зовут {person.name} ({person.job_title})! 

Возраст: {age(person.birthdate)}

Наставник: {chief.name}

Немного обо мне:
{person.description}'''
    except:
        return f'''Вот так твой профиль выглядит сейчас✨

Привет, меня зовут {person.name} ({person.job_title})! 

Возраст: {age(person.birthdate)}

Наставник: {person.chief}

Немного обо мне:
{person.description}'''


class ProfileCallback(CallbackData, prefix="profile_callbacks"):
    action: str
    value: Optional[str]

class Profile(Person):

    def __init__(self):
        pass

    def get_keyboard(buttons: list, buttons_in_row: int):
        builder = InlineKeyboardBuilder()
        builder.button(text="Изменить профиль", callback_data=ProfileCallback(action="change_profile", value="Изменить профиль"))
        builder.button(text="Статистика", callback_data=ProfileCallback(action="statistics", value="Статистика"))
        builder.button(text="Сделки", callback_data=ProfileCallback(action="deals", value="Сделки"))
        builder.button(text="Команда", callback_data=ProfileCallback(action="team", value="Команда"))
        builder.adjust(2)
        return builder.as_markup()