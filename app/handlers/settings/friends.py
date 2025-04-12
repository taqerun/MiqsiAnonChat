import inspect

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.core import commands
from app.keyboards import create_keyboard, friends_list_keyboard, make_confirm_keyboard
from app.database.models import User
from app.services.user_friends_services import UserFriendsService


friends_settings_router = Router()


@commands.setup_command(friends_settings_router, 'friends', '👥 My friends')
@friends_settings_router.callback_query(lambda c: c.data == 'friends_list')
async def friends_list(event: Message | CallbackQuery, user: User):
    """
    Prompt the user to select a language using inline keyboard.
    """
    keyboard = friends_list_keyboard(user.friends)
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(_("<b>Choose your friend:</b>"), reply_markup=keyboard)
    else:
        await event.reply(_("<b>Choose your friend:</b>"), reply_markup=keyboard)


@friends_settings_router.callback_query(lambda c: c.data.startswith('friend:'))
async def friend_menu(callback: CallbackQuery):
    data = callback.data.split(':')
    friend_name = data[1]
    keyboard = create_keyboard(
        [
            {
                'text': '✏ ' + _('Rename'),
                'data': f'friend_menu:rename:{friend_name}'
            },
            {
                'text': '💬 ' + _('Request for dialog'),
                'data': f'friend_menu:request_for_dialog:{friend_name}'
            },
            {
                'text': '❌ ' + _('Delete'),
                'data': f'friend_menu:delete:{friend_name}'
            },
            {
                'text': '◀ ' + _('Back'),
                'data': 'friends_list'
            }

        ]
    )
    await callback.message.edit_text(
        text=_('<b>Choose action with your friend: {name}</b>').format(name=friend_name),
        reply_markup=keyboard
    )


@friends_settings_router.callback_query(lambda c: c.data.startswith('friend_menu'))
async def friend_settings(callback: CallbackQuery, friends_service: UserFriendsService):
    data = callback.data.split(':')
    action = data[1]
    friend_name = data[2]
    confirm = 'confirm' in data
    params = data[-1].split('|') if len(data) > 3 else None

    action_name = action.replace("_", " ").capitalize()
    action_message_template = f'<b>{friend_name}</b>\n<b>{action_name}</b>' + '\n\n {message}'

    friend_id = friends_service.get_friend_id_by_name(friend_name)

    if friend_id:
        if action:
            if not confirm:
                confirm_keyboard = make_confirm_keyboard(callback.data, f'friend:{friend_name}')
                message = _('Are you sure?')

                await callback.answer(message)
                await callback.message.edit_text(
                    text=action_message_template.format(message=message),
                    reply_markup=confirm_keyboard
                )
            else:
                friend_action_method = getattr(friends_service, action, None)

                if callable(friend_action_method):
                    if len(inspect.signature(friend_action_method).parameters) > 1:
                        await friend_action_method(friend_name, *params)
                    else:
                        if params:
                            res: dict = await friend_action_method(friend_name)

                            for user_id, user_message in res.items():
                                if user_id == callback.from_user.id:
                                    await callback.answer(user_message)
                                    await callback.message.delete()

                                await callback.bot.send_message(user_id, user_message)
