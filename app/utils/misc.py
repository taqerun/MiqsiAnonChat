import os

from aiogram.utils.i18n import gettext as _


INTERESTS_RESET_KEY = 'reset_interests'


def chunked(seq, size):
    """Split sequence into evenly sized chunks."""
    return [seq[i:i + size] for i in range(0, len(seq), size)]


def language_flag(lang_code: str) -> str:
    if len(lang_code) != 2:
        return ''

    lang_code = lang_code.replace('en', 'us')

    return ''.join(chr(0x1F1E6 + ord(c.upper()) - ord('A')) for c in lang_code)


def get_available_locales(locales_dir="locales") -> list[str]:
    return [
        name for name in os.listdir(locales_dir)
        if os.path.isdir(os.path.join(locales_dir, name))
    ]


def get_available_interests() -> dict:

    interests = {
        'anime': _('anime'),
        'music': _('music'),
        'games': _('games'),
        'books': _('books'),
        'travels': _('travels'),
        'pets': _('pets'),
        'roleplay': _('roleplay'),
        'memes': _('memes'),
        'sport': _('sport')
    }
    return interests
