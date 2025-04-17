# app/services/dialog/message_formatter.py

from typing import Optional

from aiogram.utils.i18n import gettext as _
from app.utils import HTML, get_available_interests


class DialogMessageFormatter:
    def format_interests(self, interests: list[str]) -> str:
        if not interests:
            return ''
        joined = ', '.join(_(i) for i in interests)
        return HTML.b('🧩 ' + f'{_("Common interests")}: {joined}')

    def format_found_header(self, friend_name: Optional[str]) -> str:
        return (
            '👥 ' + _("It's your friend {friend_name}!\n").format(friend_name=HTML.b(friend_name))
            if friend_name else
            HTML.b('🎉 ' + _('A conversational partner has been found!\n'))
        )

    def format_commands(self) -> str:
        return '\n'.join([
            f'{HTML.b("/stop")} — ' + _('stop the dialog'),
            f'{HTML.b("/next")} — ' + _('find the next partner'),
            f'{HTML.b("/friend")} — ' + _('add user as a friend')
        ])

    def format_queue_waiting(self) -> str:
        return '⏳ ' + _('You are already in the queue. Please wait...')

    def format_stopped(self) -> str:
        return '🛑 ' + _('Dialog search stopped')

    def format_user_left(self) -> str:
        return '💬 ' + _('You have left the dialog')

    def format_partner_left(self) -> str:
        return '👤 ' + _('Your partner left the dialog')

    def format_searching(self, interests: list[str], mode: str) -> str:
        available_interests = get_available_interests()
        localized_interests = [available_interests[interest] for interest in interests]
        interests_part = '' if not interests else ' '+ _('with interests') + ': ' + ', '.join(localized_interests)
        mode_part = HTML.i(_(mode.replace('-', ' ').capitalize()))
        return '🔎 ' + _('Looking for a dialog partner{interests}\nDialog mode: {mode}').format(
            interests=interests_part, mode=mode_part
        )

    def format_unknown(self) -> str:
        return '🤖 ' + _('Oops... Something went wrong.')
