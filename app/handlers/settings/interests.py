from aiogram import Router, types
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import commands
from app.keyboards import interests_keyboard
from app.database.models import User, QueueUser
from app.utils.misc import get_available_interests, INTERESTS_RESET_KEY
from app.utils import HTML


interests_router = Router()


@commands.setup_command(interests_router, 'interests', '🧩 Set your interests')
async def handle_interests_command(message: Message, user: User):
    """
    Entry point for selecting interests.
    Supports both command and button callback triggers.
    """
    keyboard = interests_keyboard(user.interests)  # type: ignore

    await message.reply(HTML.b(_("Choose your interests")), reply_markup=keyboard)


@interests_router.callback_query(lambda c: c.data in get_available_interests().keys() or c.data == INTERESTS_RESET_KEY)
async def handle_interest_selection(callback: types.CallbackQuery, session: AsyncSession, user: User):
    """
    Handles toggle/reset of selected interests.
    Updates both User and QueueUser models.
    """
    chosen_interest = callback.data.strip()

    interests = user.interests or []

    if chosen_interest == INTERESTS_RESET_KEY:
        interests = []
    elif chosen_interest in user.interests:
        interests.remove(chosen_interest)
    else:
        interests.append(chosen_interest)

    if user.queue_entry:
        queue_user = await session.get(QueueUser, user.id)

        if queue_user:
            queue_user.interests = interests

    user.interests = interests

    await session.commit()

    await callback.message.edit_reply_markup(reply_markup=interests_keyboard(interests))
