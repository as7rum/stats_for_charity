from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from contextlib import suppress

from handlers.profile import ProfileCallback, update_profile_page, profile, send_profile_page
from google_sheets_services.person_sheets_service import PersonSheetsService
from models.valid import is_valid
from config.messages import ADD_NAME_ERROR_MESSAGE

router = Router()

service = PersonSheetsService()

class ProfileSettingsStates(StatesGroup):
    changing_name = State()
    getting_new_name = State()
    changing_job_title = State()
    getting_new_job_title = State()
    changing_birthdate = State()
    getting_new_birthdate = State()
    changing_description = State()
    getting_new_description = State()

accept = ['изменить']
cancel = ['отмена']

change_kb = [
        [
            types.KeyboardButton(text="Изменить"),
            types.KeyboardButton(text="Отмена"),
        ],
    ]
change_keyboard = types.ReplyKeyboardMarkup(
           keyboard=change_kb,
           resize_keyboard= True)

@router.callback_query(ProfileCallback.filter(F.action == "change_name"))
async def callbacks_change_name(callback: types.CallbackQuery, state: FSMContext):
    global service
    global person

    person = service.get_person_by_username(callback.from_user.username)
    #тебя зовут Айнар, хочешь изменить имя?
    #введи новое имя
    #Добавить клавиатуру для выбора, 
    await state.set_state(ProfileSettingsStates.changing_name)
    await callback.message.answer(f'Тебя зовут {person.name}. Хочешь изменить?', reply_markup=change_keyboard)
    await callback.answer()#(text="Меняем имя.")

@router.message(ProfileSettingsStates.changing_name, F.text.lower().in_(cancel))
async def check_add_another_name(message: types.Message, state: FSMContext):
    await message.answer('Хорошо', 
    reply_markup = types.ReplyKeyboardRemove())
    await state.clear()
    await send_profile_page(message.from_user.username, message.from_user.id)

@router.message(ProfileSettingsStates.changing_name, F.text.lower().in_(accept))
async def check_add_name(message: types.Message, state: FSMContext):
    global person

    await message.answer('Хорошо', 
    reply_markup = types.ReplyKeyboardRemove())
    await message.answer('Отправь мне новое имя', reply_markup= types.ForceReply(
        input_field_placeholder= 'Имя Фамилия'))
    await state.set_state(ProfileSettingsStates.getting_new_name)

@router.message(ProfileSettingsStates.getting_new_name)
async def add_name(message: types.Message, state: FSMContext):
    global service
    global person

    if is_valid(r'^([А-Я][а-я]*[ ]?){1,3}$', message.text):
        person.name = message.text
        service.person_data_update(person)
        await message.answer('Имя обновлено')
        await state.clear()
        await send_profile_page(message.from_user.username, message.from_user.id)
        return
    await message.answer(ADD_NAME_ERROR_MESSAGE)
    await state.set_state(ProfileSettingsStates.getting_new_name)


@router.callback_query(ProfileCallback.filter(F.action == "change_job_title"))
async def callbacks_change_job_title(callback: types.CallbackQuery, callback_data: ProfileCallback):
    await callback.answer(text="Меняем должность.")

@router.callback_query(ProfileCallback.filter(F.action == "change_birthdate"))
async def callbacks_change_birthdate(callback: types.CallbackQuery, callback_data: ProfileCallback):
    await callback.answer(text="Меняем дату рождения.")

@router.callback_query(ProfileCallback.filter(F.action == "change_description"))
async def callbacks_change_description(callback: types.CallbackQuery, callback_data: ProfileCallback):
    await callback.answer(text="Меняем описание.")