from aiogram import Router
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from app.core import commands
from app.keyboards import stop_button_keyboard, dialog_menu_keyboard
from app.services.builders.dialog_builder import DialogContext
from app.services.utils_services import UtilsServices
from app.utils import HTML


search_router = Router()


@commands.setup_command(search_router, 'search', '🔎 Search dialog')
async def search_dialog(message: Message, dialog_ctx: DialogContext, utils_service: UtilsServices):
    
    """
    Handles the /search command to initiate a dialog search.
    If the user is already in a dialog, sends a message indicating this.
    Otherwise, starts the dialog search process and sends appropriate messages
    with the relevant keyboard based on the current dialog state.
    """
    if dialog_ctx.service.current_dialog:
        await message.reply('❌ ' + HTML.b(_('You already in dialog now')))
        return

    res = await dialog_ctx.service.start_dialog_search()
    keyboard = stop_button_keyboard()

    if dialog_ctx.service.current_dialog:
        keyboard = dialog_menu_keyboard(dialog_ctx.service.is_friends)

    await utils_service.send_messages(res, keyboard)
