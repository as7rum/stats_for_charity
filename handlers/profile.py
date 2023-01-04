from aiogram import Router
from aiogram.filters.text import Text
from aiogram.filters.command import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import pprint

from google_sheets_services.person_sheets_service import PersonSheetsService
from models.person import Person
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
