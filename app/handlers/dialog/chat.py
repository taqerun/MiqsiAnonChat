from aiogram import Router, types
from aiogram.utils.i18n import gettext as _

from app.core.config import redis
from app.database.models import User
from app.services.builders.dialog_builder import DialogContext
from app.services.dialog.dialog_forward_services import DialogForwardService
from app.states import DialogStates


chat_router = Router()


@chat_router.message(DialogStates.dialog)
async def relay_dialog_message(
    message: types.Message,
    dialog_ctx: DialogContext,
    user: User,
):
    """
    Handles any message from the user in the DialogStates.dialog state
    and forwards it to the current dialog partner, if the message is not a command,
    and if it matches the user's dialog mode (voice-only, video-only, or both).
    """
    if message.text and message.text.startswith("/"):
        return

    forward_service = DialogForwardService(message.bot, redis, dialog_ctx.service.current_dialog.id)

    match user.mode:
        case "only-voice-messages" if not message.voice:
            await message.reply('🎤 ' + _("In your dialog mode, only voice messages are allowed."))
            return
        case "only-video-messages" if not message.video:
            await message.reply( '📹 ' + _("In your dialog mode, only video messages are allowed."))
            return
        case "voice-and-video-messages" if not (message.voice or message.video):
            await message.reply('🎥🎤 ' + _("In this mode, only voice or video messages are allowed."))
            return

    await forward_service.forward(message=message, recipient_id=dialog_ctx.partner.id)


@chat_router.edited_message(DialogStates.dialog)
async def edit_dialog_message(message, dialog_ctx: DialogContext):
    forward_service = DialogForwardService(message.bot, redis, dialog_ctx.service.current_dialog.id)

    await forward_service.edit_message(message, dialog_ctx.partner.id)
