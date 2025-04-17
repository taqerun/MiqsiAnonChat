from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.core import commands
from aiogram.fsm.context import FSMContext
from app.states import FriendsStates
from app.keyboards import create_keyboard, friends_list_keyboard, make_confirm_keyboard
from app.database.models import User
from app.services.user_friends_services import UserFriendsService
from app.services.utils_services import UtilsServices
from app.utils import HTML


friends_settings_router = Router()


@commands.setup_command(friends_settings_router, 'friends', '👥 My friends')
@friends_settings_router.callback_query(lambda c: c.data == 'friends_list')
async def friends_list(event: Message | CallbackQuery, user: User, state: FSMContext):
    """
    Prompt the user to select a language using inline keyboard.
    """
    keyboard = friends_list_keyboard(user.friends)
    text = HTML.b(_('Choose your friend')) + ': ' if len(user.friends) else HTML.b(_("Now you don't have any friends")) + ' 😢'
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(_(text), reply_markup=keyboard)
    else:
        await event.reply(_(text), reply_markup=keyboard)


@friends_settings_router.callback_query(lambda c: c.data.startswith('friend:'))
async def friend_menu(callback: CallbackQuery, state: FSMContext):
    await state.update_data(message_for_edit=callback.message.message_id)
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
        text=HTML.b(_('Choose action for: {name}')).format(name=friend_name),
        reply_markup=keyboard
    )


@friends_settings_router.callback_query(lambda c: c.data.startswith('friend_menu'))
async def friend_settings(callback: CallbackQuery, friends_service: UserFriendsService, user: User, utils_service: UtilsServices):
    data = callback.data.split(':')
    action = data[1]
    friend_name = data[2]
    confirm = 'confirm' in data
    action_name = action.replace("_", " ").capitalize()
    action_message_template = HTML.b(action_name) + ': ' + HTML.b(friend_name) + '\n\n {message}'

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
                action_func = getattr(friends_service, action)
                res = await action_func(friend_name)
                await utils_service.send_messages(
                    res,
                    edit=True,
                    message_for_edit={'mid': callback.message.message_id, 'uid': callback.from_user.id})
    else:
        await callback.answer(_('Friend is not found'))
        await friends_list(callback.message, user)
        await callback.message.delete()



@friends_settings_router.message(FriendsStates.rename)
async def rename_friend(message: Message, friends_service: UserFriendsService, state: FSMContext, utils_service: UtilsServices):
    await state.update_data(new_name=message.text)

    state_data = await state.get_data()
    name = state_data.get('name')
    mid = state_data.get('message_for_edit')
    res = await friends_service.rename(name)
    await utils_service.send_messages(
        res,
        edit=True,
        message_for_edit={'mid': mid, 'uid': message.from_user.id}
    )
