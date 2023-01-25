from aiogram import Router, types, F
from handlers.profile import ProfileCallback, update_profile

router = Router()

@router.callback_query(ProfileCallback.filter(F.action == "deals"))
async def callbacks_deals(callback: types.CallbackQuery, callback_data: ProfileCallback):
    await update_profile(callback.message, 'Здесь должны быть сделки')
    await callback.answer(text="Открываем сделки.")