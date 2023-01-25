from aiogram import Router, types, F
from handlers.profile import ProfileCallback, update_profile

router = Router()

@router.callback_query(ProfileCallback.filter(F.action == "statistics"))
async def callbacks_statistics(callback: types.CallbackQuery, callback_data: ProfileCallback):
    await update_profile(callback.message, 'Здесь должна быть статистика')
    await callback.answer(text="Открываем статистику.")