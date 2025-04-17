from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import commands
from app.database import User
from app.keyboards import dialog_menu_keyboard, make_confirm_keyboard
from app.services.builders.dialog_builder import DialogContext
from app.services.friends_services import FriendsService
from app.states import DialogStates
from app.utils import HTML


friend_router = Router()


@commands.setup_command(friend_router, 'friend', '👥 Add user to friends', StateFilter(DialogStates.dialog))
@friend_router.callback_query(lambda c: c.data == 'friend', DialogStates.dialog)
async def friend_request(
        message: Message,
        user: User,
        dialog_ctx: DialogContext,
        session: AsyncSession
):
    """
    Handles /friend or "Add to friends" button in the dialog menu to send a friend request.

    :param message: Telegram message object.
    :param user: User who sent a friend request.
    :param dialog_ctx: Dialog context object, containing the current dialog partner.
    :param session: SQLAlchemy session object.
    :return: None
    """

    if not dialog_ctx.service.current_dialog:
        return await message.answer(HTML.b(_("You haven't dialog partner")))

    friends_service = FriendsService(user, dialog_ctx.partner, session)

    if friends_service.is_friends:
        await message.reply('❌ ' + HTML.b(_('You are already friends now')))
        return


    await message.reply(
        HTML.b(_(
            'You have sent a friend request\n\n'
            'Waiting for a reply from the person you are talking to...'
        ))
    )

    keyboard = make_confirm_keyboard(
        f'friend_request:accept:{dialog_ctx.service.current_dialog.id}',
        f'friend_request:decline:{dialog_ctx.service.current_dialog.id}'
    )

    await message.bot.send_message(
        dialog_ctx.partner.id,
        text=HTML.b(_('A user sent you a friend request\n\n'
               'Would you like to be anonymous friends?')),
        reply_markup=keyboard
    )


@friend_router.callback_query(lambda c: c.data.startswith('friend_request'), DialogStates.dialog)
async def friend_request_confirmation(
        callback: CallbackQuery,
        user: User,
        dialog_ctx: DialogContext,
        session: AsyncSession
):
    """
    Handles a friend request response from another user.

    :param callback: Telegram callback query object.
    :param user: User who responded to the friend request.
    :param dialog_ctx: Dialog context object, containing the current dialog partner.
    :param session: SQLAlchemy session object.
    :return: None
    """
    data = callback.data.split(':')
    decision = data[1]
    dialog_id = data[2]
    friends_service = FriendsService(user, dialog_ctx.partner, session)

    if int(dialog_id) != dialog_ctx.service.current_dialog.id:
        await callback.message.delete()
        return

    match decision:
        case 'accept':
            messages = await friends_service.make_friends()
            keyboard = dialog_menu_keyboard(friends_service.is_friends)

            await callback.message.edit_text(messages[user.id], reply_markup=None)
            await callback.bot.send_message(chat_id=dialog_ctx.partner.id, text=messages[dialog_ctx.partner.id], reply_markup=keyboard)

        case 'decline':
            await callback.message.edit_text('❌ ' + HTML.b(_('You declined a friendship request</b>'), reply_markup=None))
            await callback.bot.send_message(
                chat_id=dialog_ctx.partner.id,
                text='❌ ' + HTML.b(_("The person you're talking to has declined your friendship request"))
            )
