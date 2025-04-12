from typing import Optional

from aiogram.utils.i18n import gettext as _

from app.database import User
from app.states import DialogStates


class DialogNotificationService:
    @staticmethod
    def _format_interests(interests: list[str]) -> str:
        if not interests:
            return ''
        joined = ', '.join(_(i) for i in interests)
        return f'🧩 <b>{_("Common interests")}:</b> {joined}'

    @staticmethod
    def _format_found_header(friend_name: Optional[str]) -> str:
        return (
            _("👥 It's your friend <b>{friend_name}</b>!\n").format(friend_name=friend_name)
            if friend_name else
            _('🎉 <b>A conversational partner has been found!</b>\n')
        )

    @staticmethod
    def _format_commands() -> str:
        return '\n'.join([
            '<b>/stop</b> — ' + _('stop the dialog'),
            '<b>/next</b> — ' + _('find the next partner'),
            '<b>/friend</b> — ' + _('add user as a friend')
        ])

    def generate(
        self,
        before_state: Optional[str],
        after_state: Optional[str],
        user: User,
        partner_id: Optional[int] = None,
        friend_names: Optional[dict[int, str]] = None
    ) -> dict[int, str]:
        friend_names = friend_names or {}
        messages: dict[int, str] = {}

        uid = user.id
        partner_name = friend_names.get(partner_id)
        user_name = friend_names.get(uid)

        def build_found_message(name: Optional[str]) -> str:
            return '\n'.join(filter(None, [
                self._format_found_header(name),
                self._format_interests(user.interests),
                self._format_commands()
            ]))

        match after_state:
            case None if before_state == DialogStates.queue.state:
                messages[uid] = _('🛑 <b>Dialog search stopped.</b>')

            case None if before_state == DialogStates.dialog.state:
                messages[uid] = _('💬 <b>You have left the dialog.</b>')
                if partner_id:
                    messages[partner_id] = _('👤 <b>Your partner left the dialog.</b>')

            case DialogStates.dialog.state:
                messages[uid] = build_found_message(user_name)
                if partner_id:
                    messages[partner_id] = build_found_message(partner_name)

            case DialogStates.queue.state if before_state != DialogStates.queue.state:
                interests = (
                    '' if not user.interests
                    else _(' with interests: ') + ', '.join(user.interests)
                )
                messages[uid] = _(
                    '🔎 <b>Looking for a dialog partner{interests}\nDialog mode:</b> {mode}'
                ).format(interests=interests, mode=user.mode)

            case DialogStates.queue.state if before_state == DialogStates.queue.state:
                messages[uid] = _('⏳ <b>You are already in the queue. Please wait...</b>')

            case _:
                messages[uid] = _('🤖 <b>Oops... Something went wrong.</b>')

        return messages
