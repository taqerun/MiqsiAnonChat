from typing import Union

from aiogram import types, Router
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import commands
from app.database import User
from app.keyboards import modes_keyboard


mode_router = Router()


available_modes = (
    'default',
    'voice',
    'video',
    'voice-and-video'
)


@commands.setup_command(mode_router, 'mode', '💬 Change dialogs mode')
async def handle_stop_command(message: Message, user: User):
    """
    Allows the user to stop dialog or queue at any FSM state.
    Handles both /stop command and "❌ Stop" button.
    """
    keyboard = modes_keyboard(selected=user.mode)
    await message.reply(_('Choose dialog mode:'), reply_markup=keyboard)


@mode_router.callback_query(lambda c: c.data in available_modes)
async def set_mode(callback: CallbackQuery, user: User, session: AsyncSession):
    selected_mode = callback.data
    current_mode = user.mode

    if selected_mode != current_mode:
        user.mode = selected_mode
        keyboard = modes_keyboard(selected=current_mode)

        await session.commit()

        await callback.message.edit_reply_markup(reply_markup=keyboard)
