# app/services/dialog/notification_service.py

from typing import Optional

from app.database import User
from app.states import DialogStates
from app.services.dialog.message_formatter import DialogMessageFormatter
from app.utils import HTML


class DialogNotificationService:
    def __init__(self, formatter: DialogMessageFormatter):
        self.formatter = formatter

    def generate(
        self,
        before_state: Optional[str],
        after_state: Optional[str],
        user: User,
        partner_id: Optional[int] = None,
        friend_names: Optional[dict[int, str]] = None
    ) -> dict[int, str]:
        messages = {}
        uid = user.id
        friend_names = friend_names or {}

        user_name = friend_names.get(uid)
        partner_name = friend_names.get(partner_id)

        def build_found_message(name: Optional[str]) -> str:
            return '\n'.join(filter(None, [
                self.formatter.format_found_header(name),
                self.formatter.format_interests(user.interests),
                self.formatter.format_commands()
            ]))

        match after_state:
            case None if before_state == DialogStates.queue.state:
                messages[uid] = self.formatter.format_stopped()

            case None if before_state == DialogStates.dialog.state:
                messages[uid] = self.formatter.format_user_left()
                if partner_id:
                    messages[partner_id] = self.formatter.format_partner_left()

            case DialogStates.dialog.state:
                messages[uid] = build_found_message(user_name)
                if partner_id:
                    messages[partner_id] = build_found_message(partner_name)

            case DialogStates.queue.state if before_state != DialogStates.queue.state:
                messages[uid] = self.formatter.format_searching(user.interests, user.mode)

            case DialogStates.queue.state if before_state == DialogStates.queue.state:
                messages[uid] = self.formatter.format_queue_waiting()

            case _:
                messages[uid] = self.formatter.format_unknown()

        return {k: HTML.b(v) for k, v in messages.items()}
