from aiogram import Router, types, F
from handlers.profile import ProfileCallback, update_profile
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.callback_query(ProfileCallback.filter(F.action == "team"))
async def callbacks_team(callback: types.CallbackQuery, callback_data: ProfileCallback):
    await update_profile(callback.message, 'Здесь должен быть список членов команды')
    await callback.answer(text="Загружаем всех членов команды.")