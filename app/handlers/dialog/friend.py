from typing import Optional

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


friend_router = Router()


@commands.setup_command(friend_router, 'friend', '👥 Add user to friends', StateFilter(DialogStates.dialog))
@friend_router.callback_query(lambda c: c.data == 'friend', DialogStates.dialog)
async def friend_request(
        message: Message,
        user: User,
        dialog_ctx: DialogContext,
        session: AsyncSession
):
    if not dialog_ctx.service.current_dialog:
        return await message.answer("You haven't dialog partner")

    friends_service = FriendsService(user, dialog_ctx.partner, session)

    if friends_service.is_friends:
        await message.reply(_('<b>❌ You are already friends now</b>'))
        return


    await message.reply(
        _(
            '<b>You have sent a friend request</b>\n\n'
            '<i><b>Waiting for a reply from the person you are talking to...</b></i>'
        )
    )

    keyboard = make_confirm_keyboard(
        f'friend_request:accept:{dialog_ctx.service.current_dialog.id}',
        f'friend_request:decline:{dialog_ctx.service.current_dialog.id}'
    )

    await message.bot.send_message(
        dialog_ctx.partner.id,
        text=_('<b>A user sent you a friend request</b>\n\n'
             '<i><b>Would you like to be anonymous friends?</b></i>'),
        reply_markup=keyboard
    )


@friend_router.callback_query(lambda c: c.data.startswith('friend_request'), DialogStates.dialog)
async def friend_request_confirmation(
        callback: CallbackQuery,
        user: User,
        dialog_ctx: DialogContext,
        session: AsyncSession
):
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
            await callback.message.edit_text(_('<b>❌ You declined a friendship request</b>'), reply_markup=None)
            await callback.bot.send_message(
                chat_id=dialog_ctx.partner.id,
                text=_("<b>❌ The person you're talking to has declined your friendship request</b>")
            )
