from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import create_user
from app.database.models import User
from app.keyboards import main_menu_keyboard
from app.utils import HTML


start_router = Router()


@start_router.message(CommandStart())
async def handle_start_command(message: types.Message, session: AsyncSession):
    """
    Handles the /start command.
    Creates the user in the database if they are new and sends welcome message.
    """
    # Check if user already exists in the database
    result = await session.execute(select(User).where(User.id == message.from_user.id))
    user = result.scalar_one_or_none()

    if user is None:
        await create_user(user_id=message.from_user.id, locale=message.from_user.language_code or "en", session=session)

    return await message.reply(
        HTML.b(_("Welcome to Miqsi Anon Chat!\n\n")) +
        f"{HTML.b('/search')} — {_('to find someone to chat with')}\n"
        f"{HTML.b('/language')} — {_('to change bot language')}\n"
        f"{HTML.b('/interests')} — {_('to set your interests')}",
        reply_markup=main_menu_keyboard()
    )
