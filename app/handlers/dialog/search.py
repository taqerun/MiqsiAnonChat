from aiogram import Router
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from app.core import commands
from app.database import User
from app.keyboards import stop_button_keyboard, dialog_menu_keyboard
from app.services.builders.dialog_builder import DialogContext
from app.services.utils_services import UtilsServices

search_router = Router()


@commands.setup_command(search_router, 'search', '🔎 Search dialog')
async def search_dialog(message: Message, dialog_ctx: DialogContext, utils_service: UtilsServices, user: User):
    """
    Handles /search or /next command or buttons to find a new dialog partner.
    Ends previous dialog (if any), updates states, and replies accordingly.
    """
    if dialog_ctx.service.current_dialog:
        await message.reply(_('<b>❌ You already in dialog now</b>'))
        return

    res = await dialog_ctx.service.start_dialog_search()
    keyboard = stop_button_keyboard()

    if dialog_ctx.service.current_dialog:
        keyboard = dialog_menu_keyboard(dialog_ctx.service.is_friends)

    await utils_service.send_messages(res, keyboard)
