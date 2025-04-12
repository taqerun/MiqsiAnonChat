from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


confirm_router = Router()


@confirm_router.callback_query(lambda c: c.data.startswith('confirm'))
async def handle_confirmation(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession
):
    """
    confirm:action:decision:data, data, data...
    """
    data = callback.data.split(':')
    action = data[1]
    decision = data[2]
    other_data = data[-1].split(', ')

    def confirm_keyboard(action: str, payload: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Confirm", callback_data=confirm_cb.pack(action, payload)),
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")
            ]
        ])

    match action:
        case 'delete_friend':
            friend_id = other_data[0]

            match decision:
                case 'yes':

                    await callback.answer(_('User {name} is deleted from your friends').format(name=friend_name))

                case 'no':
                    await callback.answer(_('Canceled'))
                    await callback.message.delete()

        case 'friend_request':

            match decision:
                case 'yes':
                    friend_id = other_data[0]
                    ...

                case 'no':
                    ...
