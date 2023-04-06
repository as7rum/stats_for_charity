from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from typing import Optional
from datetime import date


from models.statistics import Statistics
from google_sheets_services.statistics_sheets_service import StatisticsSheetsService
from models.valid import is_valid
from handlers.profile import ProfileCallback, send_profile_page
from config.locations import locations

router = Router()
stats = Statistics()

accept = ['да']
cancel = ['отмена']

kb_for_cancle_actions_with_stats = [
        [
            types.KeyboardButton(text="Отмена")
        ]
    ]
keyboard_for_canceling_actions_with_stats = types.ReplyKeyboardMarkup(
           keyboard=kb_for_cancle_actions_with_stats,
           resize_keyboard= True)

class LocationCallback(CallbackData, prefix="locations_callbacks"):
    action: str
    location: str

class StatisticsOptionsStates(StatesGroup):
    add_location = State()
    add_statistic = State()
    add_statistic_comments = State()

def get_stats_keyboard():
        builder = InlineKeyboardBuilder()
        builder.button(text="Добавить", callback_data=ProfileCallback(action="add_stats"))
        builder.button(text="Моя статистика", callback_data=ProfileCallback(action="my_stats"))
        builder.button(text="Моя командная статистика", callback_data=ProfileCallback(action="my_team_stats"))
        builder.button(text="Назад", callback_data=ProfileCallback(action="back"))
        builder.adjust(2)
        return builder.as_markup()

@router.callback_query(ProfileCallback.filter(F.action == "statistics"))
async def callbacks_statistics(callback: types.CallbackQuery, callback_data: ProfileCallback):
    await callback.message.edit_text('Здесь должна быть статистика', parse_mode='HTML', reply_markup=get_stats_keyboard())
    await callback.answer(text="Открываем статистику.")

def location_keyboard():
    global locations
    builder = InlineKeyboardBuilder()
    for location in locations:
        builder.button(text=location, callback_data=LocationCallback(action='chose_location', location=location))
    builder.button(text="Отмена", callback_data=ProfileCallback(action="back"))
    builder.adjust(1)
    return builder.as_markup()

@router.callback_query(ProfileCallback.filter(F.action == "add_stats"))
async def add_stats(callback: types.CallbackQuery, callback_data: ProfileCallback,  state: FSMContext):
    await callback.answer(text="Подгружаем скрипты...")
    await callback.message.answer('Хорошо, для начала выбери территорию:', reply_markup=location_keyboard())
    await state.set_state(StatisticsOptionsStates.add_location)

@router.callback_query(StatisticsOptionsStates.add_location, LocationCallback.filter(F.action == "chose_location"))
async def add_stats(callback: types.CallbackQuery, callback_data: LocationCallback, state: FSMContext):
    global stats

    stats.location = callback_data.location
    await callback.message.answer('Отлично, территория выбрана.', reply_markup=keyboard_for_canceling_actions_with_stats)
    await callback.message.answer('''Отправь мне статистику в виде 
Подходы/Краткие/Закрытия/Анкеты/Хроны/Сторонники''', 
    reply_markup=types.ForceReply(input_field_placeholder='ППП/КК/ЗЗ/АА/ХХ/СС'))
    await state.set_state(StatisticsOptionsStates.add_statistic)

@router.message(StatisticsOptionsStates.add_statistic, F.text.lower().in_(cancel))
async def cancle_adding_statistics(message: types.Message, state: FSMContext):
    await message.answer('Хорошо.', 
    reply_markup = types.ReplyKeyboardRemove())
    await state.clear()
    await send_profile_page(message.from_user.username, message.from_user.id)

@router.message(StatisticsOptionsStates.add_statistic)
async def adding_statistics(message: types.Message, state: FSMContext):
    global stats
    if is_valid(r'^(\d{1,3}/){5}\d{1,3}$', message.text):
        statistics = message.text.split('/')
        stats.date = str(date.today())
        stats.username = message.from_user.username
        stats.city = 'Санкт-Петербург'
        stats.approaches = statistics[0]
        stats.shorts = statistics[1]
        stats.closings = statistics[2]
        stats.forms = statistics[3]
        stats.trust_pays = statistics[4]
        stats.supporters = statistics[5]
        await message.answer('Хорошо, статистика записана.', 
        reply_markup = types.ReplyKeyboardRemove())
        await message.answer('''Теперь отправь мне сообжение с комментариями по сегодняшнему дню.''')
        await state.set_state(StatisticsOptionsStates.add_statistic_comments)
        return
    await message.answer('Неправильный формат ввода, отправь попробуй отправить статистику еще раз.', 
    reply_markup=types.ForceReply(input_field_placeholder='ППП/КК/ЗЗ/АА/ХХ/СС'))
    await state.set_state(StatisticsOptionsStates.add_statistic)

@router.message(StatisticsOptionsStates.add_statistic_comments)
async def adding_statistics_description(message: types.Message, state: FSMContext):
    global stats
    
    stats.comments = message.text
    await message.answer('Так, описание принято, отправляю статистику.')
    service = StatisticsSheetsService()
    service.add_statistics(stats)
    person_stats = service.get_statistics_by_person_username(message.from_user.username)
    today_person_stats = next(filter(lambda x: x.date == str(date.today()), person_stats), None)
    await message.answer(f'''Статистика за сегодня ({today_person_stats.date}): 
Территория: {today_person_stats.location} 
Подходы: {today_person_stats.approaches}
Краткие: {today_person_stats.shorts}
Закрытия: {today_person_stats.closings}
Анкеты: {today_person_stats.forms}
Хроны: {today_person_stats.trust_pays}
Сторонники: {today_person_stats.supporters}''')
    await message.answer('Успешно добавлено')
    await state.clear()
    await send_profile_page(message.from_user.username, message.from_user.id)



@router.callback_query(ProfileCallback.filter(F.action == "my_stats"))
async def add_stats(callback: types.CallbackQuery, callback_data: ProfileCallback):
    await callback.answer(text="Моя статистика.")

@router.callback_query(ProfileCallback.filter(F.action == "my_team_stats"))
async def add_stats(callback: types.CallbackQuery, callback_data: ProfileCallback):
    await callback.answer(text="Статистика моей команды.")

