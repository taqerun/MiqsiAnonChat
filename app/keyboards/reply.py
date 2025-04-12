from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.i18n import gettext as _


def main_menu_keyboard(locale: str=None) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_('🔎 Search dialog', locale=locale))],
            [KeyboardButton(text=_('💬 Change dialogs mode', locale=locale))],
            [
                KeyboardButton(text=_('🧩 Set your interests', locale=locale)),
                KeyboardButton(text=_('⚙ Change bot language', locale=locale))
            ],
            [
                KeyboardButton(text=_('👥 My friends', locale=locale))
            ]
        ],

        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder=_("Choose an action", locale=locale)
    )

def dialog_menu_keyboard(is_friends: bool=False) -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text=_('🔎 Search next dialog'))
        ],
        [
            KeyboardButton(text=_('❌ Stop'))
        ],
    ]

    if not is_friends:
        buttons.append([KeyboardButton(text=_('👥 Add user to friends'))])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder=_("Choose an action")
    )


def friends_request_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_('✅ Accept friend request'))],
            [KeyboardButton(text=_('❌ Decline friend request'))]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder=_("Choose an action")
    )

def stop_button_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_('❌ Stop'))]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder=_("Choose an action")
    )


def friends_keyboard(friends) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=friend['name'])]
            for friend in friends.values()
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder=_("Choose an action")
    )
