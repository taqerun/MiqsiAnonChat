from aiogram import Router, types
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import commands
from app.keyboards import languages_keyboard, main_menu_keyboard
from app.database.models import User
from app.utils import get_available_locales
from app.utils import HTML


language_router = Router()


@commands.setup_command(language_router, 'language', '⚙ Change bot language')
async def prompt_language_selection(message: Message, user: User):
    """
    Prompt the user to select a language using inline keyboard.
    """
    await message.reply(HTML.b(_("Choose your language")), reply_markup=languages_keyboard(locale=user.locale))


@language_router.callback_query(lambda c: c.data in get_available_locales())
async def set_language(callback: types.CallbackQuery, session: AsyncSession, user: User):
    """
    Sets the new language in the user's profile if valid and different.
    """
    selected_locale = callback.data.strip()
    current_locale = user.locale

    if selected_locale != current_locale:
        user.locale = selected_locale

        await session.commit()

        text = '💬 ' + _("Language updated from {before} to {after}", locale=selected_locale).format(
                before=current_locale.upper(),
                after=selected_locale.upper()
            )

        if callback.message.reply_to_message:
            await callback.message.reply_to_message.reply(HTML.b(text), reply_markup=main_menu_keyboard(selected_locale))

        await callback.answer(text)
        await callback.message.delete()
    else:
        await callback.answer(HTML.b(_("Please choose a language different from your current one")))
