from typing import Union, Optional

from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from app.core import commands
from app.database import User
from app.keyboards import dialog_menu_keyboard, main_menu_keyboard, stop_button_keyboard
from app.services.builders.dialog_builder import DialogContext
from app.services.utils_services import UtilsServices

next_router = Router()


@commands.setup_command(next_router, 'next', '🔎 Search next dialog', StateFilter("*"))
async def next_dialog(message: Message, dialog_ctx: DialogContext, utils_service: UtilsServices):
    """
    Handles /search or /next command or buttons to find a new dialog partner.
    Ends previous dialog (if any), updates states, and replies accordingly.
    """
    if not dialog_ctx.service.current_dialog:
        await message.answer(_('<b>You are not in dialog now</b>'))
        return

    stop_res = await dialog_ctx.service.stop_dialog()

    await utils_service.send_messages(stop_res, main_menu_keyboard())

    search_res = await dialog_ctx.service.start_dialog_search()

    if dialog_ctx.user.queue_entry:
        keyboard = stop_button_keyboard()
    else:
        keyboard = dialog_menu_keyboard(dialog_ctx.service.is_friends)

    await utils_service.send_messages(search_res, keyboard)
