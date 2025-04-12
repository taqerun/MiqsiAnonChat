from aiogram import Router
from aiogram.types import Message

from app.core import commands
from app.keyboards import main_menu_keyboard
from app.services.builders.dialog_builder import DialogContext
from app.services.utils_services import UtilsServices

stop_router = Router()


@commands.setup_command(stop_router, 'stop', '❌ Stop')
async def stop_command(message: Message, dialog_ctx: DialogContext, utils_service: UtilsServices):
    """
    Allows the user to stop dialog or queue at any FSM state.
    Handles both /stop command and "❌ Stop" button.
    """

    res = await dialog_ctx.service.stop_dialog()
    keyboard = main_menu_keyboard()

    await utils_service.send_messages(res, keyboard)
