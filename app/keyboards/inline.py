from typing import List, Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from app.utils import misc, get_available_interests, INTERESTS_RESET_KEY


def chunk_buttons(buttons: List[InlineKeyboardButton], size: int = 3):
    '''
    Splits a list of buttons into rows of a given size.
    '''
    return [buttons[i:i + size] for i in range(0, len(buttons), size)]


def create_keyboard(buttons: List[dict], last_button: dict=None, size: int=1, locale: str = None) -> InlineKeyboardMarkup:
    '''
    Create a dynamic keyboard depending on context.
    '''
    def localize(text: str) -> str:
        return _(text, locale=locale) if locale else _(text)

    inline_buttons = chunk_buttons(
        [
            InlineKeyboardButton(text=button['text'], callback_data=button['data'])
            for button in buttons
        ],
        size=size
    )

    if last_button:
        inline_buttons.append([InlineKeyboardButton(text=last_button['text'], callback_data=last_button['data'])])

    return InlineKeyboardMarkup(inline_keyboard=inline_buttons)


def languages_keyboard(locale: str=None) -> InlineKeyboardMarkup:
    '''
    Create a keyboard for language selection.
    '''
    languages = misc.get_available_locales()
    languages.remove(locale)

    return create_keyboard(
        [
            {
                'text': f'{misc.language_flag(lang)} | {lang.upper()}',
                'data': lang
            } for lang in languages if lang
        ],
        size=3
    )


def interests_keyboard(user_interests: Optional[List[str]]) -> InlineKeyboardMarkup:
    '''
    Create a keyboard for selecting user interests.
    '''

    interests = get_available_interests()

    keyboard = create_keyboard(
        [
            {
                'text': '✅ ' + _(interest)
                if user_interests is not None and interest in user_interests else interests[interest],
                'data': interest
            }
            for interest in interests.keys()
        ],
        last_button={'text': '🧹 ' + _('Reset interests'), 'data': INTERESTS_RESET_KEY},
        size=3
    )

    return keyboard


def modes_keyboard(selected: str=None) -> InlineKeyboardMarkup:
    modes = [
        ('default', _('Default')),
        ('voice', _('Only voice messages')),
        ('video', _('Only video messages')),
        ('voice-and-video', _('Voice and video messages')),
    ]

    keyboard = create_keyboard([
        {
            'text': f"✅ {label}" if mode == selected else label,
            'data': mode
        }
        for mode, label in modes
    ])

    return keyboard


def friends_list_keyboard(friends: dict) -> InlineKeyboardMarkup:
    return create_keyboard(
        [
            {'text': friends[friend_id]['name'], 'data': f"friend:{friends[friend_id]['name']}"}
            for friend_id in friends.keys()
        ]
    )

def make_confirm_keyboard(data: str, back_to: str):
    return create_keyboard([
        {'text': '✅ ' + _('Confirm'), 'data': data + ':confirm'},
        {'text': '❌ ' + _('Cancel'), 'data': back_to}
    ])
