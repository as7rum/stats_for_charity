from aiogram import Router, types, F
from aiogram.filters.text import Text
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from time import sleep

from google_sheets_services.person_sheets_service import PersonSheetsService
from models.person import Person
from models.valid import is_valid, valid_date, age
from config.messages import (START_COMMAND_MESSAGE, ADD_NAME_MESSAGE, 
ADD_NAME_ERROR_MESSAGE, ADD_BIRTDATE_MESSAGE, ADD_BIRTDATE_ERROR_MESSAGE, 
ADD_CHIEF_MESSAGE, ADD_CHIEF_ERROR_MESSAGE)

router = Router()  # [1]

class AddNewUser(StatesGroup):
    add_name = State()
    check_add_name = State()
    add_birthdate = State()
    check_add_birthdate = State()
    add_chief = State()
    check_add_chief = State()
    add_job_title = State()
    add_description = State()

person: Person = None
profile = f'''Вот так твой профиль выглядит сейчас✨
Привет, меня зовут {person.name}({person.job_title})! 
Возраст: {age(person.birthdate)}
Наставник: {person.chief}
Немного обо мне:
{person.description}'''

@router.message(Command("start"))  # [2]
async def cmd_start(message: Message, state: FSMContext):
    global person
    global profile
    service = PersonSheetsService()
    person = service.get_person(message.from_user.username)
    if person == None:
        person = Person()
        person.id = message.from_user.id
        person.username = message.from_user.username
        await message.answer(START_COMMAND_MESSAGE)
        sleep(1)
        await message.answer(profile)
        sleep(1)
        await message.answer(ADD_NAME_MESSAGE, reply_markup= types.ForceReply(
        input_field_placeholder= 'Имя Фамилия'))
        await state.set_state(AddNewUser.add_name)
    else:
        await message.answer(
            f"Привет, {person.name}! Рад снова тебя видеть.")
        await message.answer(profile)


accept = ['подтвердить']
another = ['ввести заново']

check_kb = [
        [
            types.KeyboardButton(text="Подтвердить"),
            types.KeyboardButton(text="Ввести заново"),
        ],
    ]
check_keyboard = types.ReplyKeyboardMarkup(
           keyboard=check_kb,
           resize_keyboard= True)

@router.message(AddNewUser.add_name)
async def add_name(message: Message, state: FSMContext):
    global person
    if is_valid(r'^([А-Я][а-я]*[ ]?){1,3}$', message.text):
        person.name = message.text
        await message.answer(f'Тебя зовут {person.name}. Хочешь подтвердить? Или введешь имя заново?',
        reply_markup = check_keyboard)
        await state.set_state(AddNewUser.check_add_name)
        return
    await message.answer(ADD_NAME_ERROR_MESSAGE)
    await state.set_state(AddNewUser.add_name)

@router.message(AddNewUser.check_add_name, F.text.lower().in_(another))
async def check_add_another_name(message: Message, state: FSMContext):
    await message.answer('Ага, хорошо! Введи другое имя.', 
    reply_markup = types.ReplyKeyboardRemove())
    await state.set_state(AddNewUser.add_name)

@router.message(AddNewUser.check_add_name, F.text.lower().in_(accept))
async def check_add_name(message: Message, state: FSMContext):
    global profile

    await message.answer('Ага, отлично!', 
    reply_markup = types.ReplyKeyboardRemove())
    sleep(1)
    await message.answer(profile)
    await message.answer(ADD_BIRTDATE_MESSAGE, reply_markup= types.ForceReply(
    input_field_placeholder= 'ДД.ММ.ГГГГ'))
    await state.set_state(AddNewUser.add_birthdate)

@router.message(AddNewUser.add_birthdate)
async def add_birthdate(message: Message, state: FSMContext):
    global person
    valid_match = is_valid(r'^(\d{2})\.(\d{2})\.(\d{4})$', message.text)
    if valid_date(*valid_match):
        person.birthdate = message.text
        await message.answer(f'Ты родился {person.birthdate}. Все правильно? Или введем заново?',
        reply_markup = check_keyboard)
        await state.set_state(AddNewUser.check_add_birthdate)
        return
    await message.answer(ADD_BIRTDATE_ERROR_MESSAGE)
    await state.set_state(AddNewUser.add_birthdate)

@router.message(AddNewUser.check_add_birthdate, F.text.lower().in_(another))
async def check_add_another_birthdate(message: Message, state: FSMContext):
    await message.answer('Ага, хорошо! Итак, ты родился...', 
    reply_markup = types.ReplyKeyboardRemove())
    await state.set_state(AddNewUser.add_birthdate)

@router.message(AddNewUser.check_add_birthdate, F.text.lower().in_(accept))
async def check_add_birthdate(message: Message, state: FSMContext):
    global profile

    await message.answer('Все, хорошо!', 
    reply_markup = types.ReplyKeyboardRemove())
    sleep(1)
    await message.answer(profile)
    await message.answer(ADD_CHIEF_MESSAGE, reply_markup= types.ForceReply(
    input_field_placeholder= '@username'))
    await state.set_state(AddNewUser.add_chief)

@router.message(AddNewUser.add_chief)
async def add_chief(message: Message, state: FSMContext):
    global person
    service = PersonSheetsService()
    if is_valid(r'^@\w*$', message.text):
        person.chief = message.text
        chief_username = person.chief.split('@')[1]
        chief_person = service.get_person(chief_username)
        if chief_person:
            # Добавить person в список team
            chief_team = chief_person.team
            chief_team.append(person.username)
            chief_person.team = chief_team


        await message.answer(f'Тебя зовут {person.name}. Хочешь подтвердить? Или введешь имя заново?',
        reply_markup = check_keyboard)
        await state.set_state(AddNewUser.check_add_name)
        return
    await message.answer(ADD_CHIEF_ERROR_MESSAGE)
    await state.set_state(AddNewUser.add_chief)

@router.message(AddNewUser.add_job_title)
async def add_job_title(message: Message, state: FSMContext):
    global person
    person.job_title = message.text
    await message.answer('Добавьте какое-нибудь описание: ')
    await state.set_state(AddNewUser.add_description)

@router.message(AddNewUser.add_description)
async def add_description(message: Message, state: FSMContext):
    global person
    person.description = message.text
    service = PersonSheetsService()
    service.add_person(person)
    await message.answer('Вы завершили заполнение профиля!')
    await message.answer('Ваш профиль!')
    # await message.answer(profile())
    await state.clear()