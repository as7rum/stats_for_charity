from aiogram import Router, types, F
from aiogram.filters.text import Text
from aiogram.filters.command import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from time import sleep

from contextlib import suppress
from typing import Optional

from google_sheets_services.person_sheets_service import PersonSheetsService
from bot import bot
from handlers.profile import person_current_profile, profile
from models.person import Person
from models.valid import is_valid, valid_date, age
from config.messages import (START_COMMAND_MESSAGE, ADD_NAME_MESSAGE, 
ADD_NAME_ERROR_MESSAGE, ADD_BIRTHDATE_MESSAGE, ADD_BIRTHDATE_ERROR_MESSAGE, 
ADD_CHIEF_MESSAGE, ADD_CHIEF_ERROR_MESSAGE, ADD_JOB_TITLE_MESSAGE)

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

person = Person()

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


@router.message(Command("start"))  # [2]
async def cmd_start(message: Message, state: FSMContext):
    global person
    service = PersonSheetsService()
    person = service.get_person(message.from_user.id)
    if person == None:
        person = Person()
        person.id = message.from_user.id
        person.username = message.from_user.username
        await message.answer(START_COMMAND_MESSAGE)
        sleep(1)
        await message.answer(person_current_profile(person), parse_mode='HTML')
        sleep(1)
        await message.answer(ADD_NAME_MESSAGE, reply_markup= types.ForceReply(
        input_field_placeholder= 'Имя Фамилия'))
        await state.set_state(AddNewUser.add_name)
    else:
        await message.answer(
            f"Привет, {person.name}! Рад снова тебя видеть.")
        #router.message.register()
        person_profile = profile(person.username)
        await bot.send_message(message.from_user.id, person_profile, 
        parse_mode="HTML", reply_markup=get_profile_keyboard())
        # await message.answer(person_current_profile(person), parse_mode="HTML")


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
    global person

    await message.answer('Ага, отлично!', 
    reply_markup = types.ReplyKeyboardRemove())
    sleep(1)
    await message.answer(person_current_profile(person), parse_mode='HTML')
    await message.answer(ADD_BIRTHDATE_MESSAGE, reply_markup= types.ForceReply(
    input_field_placeholder= 'ДД.ММ.ГГГГ'))
    await state.set_state(AddNewUser.add_birthdate)

@router.message(AddNewUser.add_birthdate)
async def add_birthdate(message: Message, state: FSMContext):
    global person
    if is_valid(r'^(\d{2})\.(\d{2})\.(\d{4})$', message.text):
        if valid_date(*message.text.split('.')):
            person.birthdate = message.text
            await message.answer(f'Ты родился {person.birthdate}. Все правильно? Или введем заново?',
            reply_markup = check_keyboard)
            await state.set_state(AddNewUser.check_add_birthdate)
            return
    await message.answer(ADD_BIRTHDATE_ERROR_MESSAGE)
    await state.set_state(AddNewUser.add_birthdate)

@router.message(AddNewUser.check_add_birthdate, F.text.lower().in_(another))
async def check_add_another_birthdate(message: Message, state: FSMContext):
    await message.answer('Ага, хорошо! Итак, ты родился...', 
    reply_markup = types.ReplyKeyboardRemove())
    await state.set_state(AddNewUser.add_birthdate)

@router.message(AddNewUser.check_add_birthdate, F.text.lower().in_(accept))
async def check_add_birthdate(message: Message, state: FSMContext):
    global person

    await message.answer('Все, хорошо!', 
    reply_markup = types.ReplyKeyboardRemove())
    sleep(1)
    await message.answer(person_current_profile(person), parse_mode='HTML')
    await message.answer(ADD_CHIEF_MESSAGE, reply_markup= types.ForceReply(
    input_field_placeholder= '@username'))
    await state.set_state(AddNewUser.add_chief)

@router.message(AddNewUser.add_chief)
async def add_chief(message: Message, state: FSMContext):
    global person
    global chief_person

    service = PersonSheetsService()
    if is_valid(r'^@\w*$', message.text):
        chief = message.text
        chief_username = chief.split('@')[1]
        chief_person = service.get_person_by_username(chief_username)
        if chief_person:
            # Добавить person в список team
            person.chief = chief_username
            if chief_person.team:
                chief_team = chief_person.team.split(',')[:-1]
                team_list = chief_team
                team_list.append(message.from_user.username)
                chief_person.team = ''.join(str(x + ',') for x in team_list)
                #Перенести все отправления на сервер в конец, после завершения регистрации.
                await message.answer(f'Ага, твой лидер это {chief_person.name}, все верно?',
                reply_markup = check_keyboard)
                await state.set_state(AddNewUser.check_add_chief)
                return
            chief_person.team = message.from_user.username + ','
            await message.answer(f'Ага, твой лидер это {chief_person.name}, все верно?',
            reply_markup = check_keyboard)
            await state.set_state(AddNewUser.check_add_chief)
            return
    await message.answer(ADD_CHIEF_ERROR_MESSAGE)
    await state.set_state(AddNewUser.add_chief)

@router.message(AddNewUser.check_add_chief, F.text.lower().in_(another))
async def check_add_another_chief(message: Message, state: FSMContext):
    await message.answer('Ага, хорошо! Скинь ссылку на твоего лидера еще раз', 
    reply_markup = types.ReplyKeyboardRemove())
    await state.set_state(AddNewUser.add_chief)

user_data = {}

class JobTitleCallback(CallbackData, prefix="job_title_callbacks"):
    action: str
    value: Optional[str]


def get_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Стажер", callback_data=JobTitleCallback(action="change", value="Стажер"))
    builder.button(text="Лидер", callback_data=JobTitleCallback(action="change", value="Лидер"))
    builder.button(text="Тимлидер", callback_data=JobTitleCallback(action="change", value="Тимлидер"))
    builder.button(text="Ассистент", callback_data=JobTitleCallback(action="change", value="Ассистент"))
    builder.button(text="Менеджер", callback_data=JobTitleCallback(action="change", value="Менеджер"))
    builder.button(text="Подтвердить", callback_data=JobTitleCallback(action="finish"))
    builder.adjust(1)
    return builder.as_markup()

async def update_job_title(message: types.Message, new_value: str):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"Ваша позиция: {new_value}",
            reply_markup=get_keyboard()
        )

@router.message(AddNewUser.check_add_chief, F.text.lower().in_(accept))
async def check_add_chief(message: Message, state: FSMContext):
    global person

    await message.answer('Отлично!', 
    reply_markup = types.ReplyKeyboardRemove())
    sleep(1)
    await message.answer(person_current_profile(person), parse_mode='HTML')
    sleep(1)
    await message.answer(ADD_JOB_TITLE_MESSAGE)
    await message.answer("Ваша позиция: ", reply_markup=get_keyboard())
    await state.set_state(AddNewUser.add_job_title)

# Выбираем занимаемую позицию (должность)
@router.callback_query(JobTitleCallback.filter(F.action == "change"), AddNewUser.add_job_title)
async def callbacks_job_title_change(callback: types.CallbackQuery, callback_data: JobTitleCallback):
    # Текущее значение
    # user_value = user_data.get(callback.from_user.id, '')

    user_data[callback.from_user.id] = callback_data.value #user_value + callback_data.value
    await update_job_title(callback.message, callback_data.value)#user_value + callback_data.value)
    await callback.answer()


# Нажатие на кнопку "подтвердить"
@router.callback_query(JobTitleCallback.filter(F.action == "finish"), AddNewUser.add_job_title)
async def callbacks_job_title_finish(callback: types.CallbackQuery, state: FSMContext):
    # Текущее значение
    global person
    user_value = user_data.get(callback.from_user.id, '')
    person.job_title = user_value

    await callback.message.edit_text(f"Занимаемая вами позиция: {user_value}")
    await callback.answer()
    await state.set_state(AddNewUser.add_description)
    sleep(1)
    await bot.send_message(callback.from_user.id, '''
    Теперь давай добавим какое-нибудь описание. Напиши что-нибудь о себе и отправь мне.''')

@router.message(AddNewUser.add_description)
async def add_description(message: Message, state: FSMContext):
    global person
    global chief_person

    person.description = message.text
    service = PersonSheetsService()
    service.add_person(person)
    service.person_data_update(chief_person)
    try:
        await  bot.send_message(chief_person.id, f'''
        Поздравляю, {person.name} теперь в вашей команде!''')
        await message.answer('Поздравляю! Вы завершили заполнение профиля!')
    except:
        pass
    person_profile = profile(person.username)
    await bot.send_message(message.from_user.id, person_profile, 
        parse_mode="HTML", reply_markup=get_profile_keyboard())
    # await message.answer(person_current_profile(person), parse_mode="HTML")
    await state.clear()
