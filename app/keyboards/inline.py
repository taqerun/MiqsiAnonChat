from typing import List, Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from app.utils import misc, get_available_interests, INTERESTS_RESET_KEY


def chunk_buttons(buttons: List[InlineKeyboardButton], size: int = 3):
    '''
    Splits a list of buttons into rows of a given size.
    '''
    return [buttons[i:i + size] for i in range(0, len(buttons), size)]


def confirmation_keyboard(action: str, target_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Yes",
                callback_data=confirm_cb.new(action=action, target_id=target_id, decision="yes")
            ),
            InlineKeyboardButton(
                text="❌ No",
                callback_data=confirm_cb.new(action=action, target_id=target_id, decision="no")
            )
        ]
    ])


def languages_keyboard(locale: str=None) -> InlineKeyboardMarkup:
    '''
    Create a keyboard for language selection.
    '''
    languages = misc.get_available_locales()
    languages.remove(locale)

    buttons = chunk_buttons([
        InlineKeyboardButton(
            text=f'{misc.language_flag(lang)} | {lang.upper()}',
            callback_data=lang
        ) for lang in languages if lang
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def interests_keyboard(user_interests: Optional[List[str]]) -> InlineKeyboardMarkup:
    '''
    Create a keyboard for selecting user interests.
    '''

    interests = get_available_interests()

    buttons = [
        InlineKeyboardButton(
            text=f'✅ {interests[interest]}'
            if user_interests is not None and interest in user_interests else interests[interest],
            callback_data=interest
        ) for interest in interests.keys()
    ]

    # Create rows of 3 buttons
    rows = chunk_buttons(buttons, size=3)

    # Add a full-width reset button at the bottom
    rows.append([
        InlineKeyboardButton(
            text=_('Reset interests'),
            callback_data=INTERESTS_RESET_KEY
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def create_keyboard(buttons: List[dict] = None, _=None, command: str = None, locale: str = None, size: int=1) -> InlineKeyboardMarkup:
    '''
    Create a dynamic keyboard depending on context.
    '''
    def localize(text: str) -> str:
        return _(text, locale=locale) if locale else _(text)

    if _ and not buttons and not command:
        buttons = [
            {'text': localize('Change bot language'), 'data': 'language'},
            {'text': localize('Choose your interests'), 'data': 'interests'},
            {'text': localize('Search dialog'), 'data': 'search'},
        ]

    elif _ and not buttons and command:
        match command:
            case 'stop':
                buttons = [
                    {'text': _('Stop'), 'data': 'stop'}
                ]
            case 'dialog':
                buttons = [
                    {'text': _('Stop'), 'data': 'stop'},
                    {'text': _('Next'), 'data': 'next'}
                ]

    inline_buttons = [
        InlineKeyboardButton(text=button['text'], callback_data=button['data'])
        for button in buttons
    ]

    return InlineKeyboardMarkup(inline_keyboard=chunk_buttons(inline_buttons, size=size))


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