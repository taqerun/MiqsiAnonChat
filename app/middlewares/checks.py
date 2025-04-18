from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.database import create_user
from app.database.utils import is_user_exist


class ChecksMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        This middleware creates a new user in the database if the user does not exist yet.

        The locale of the user is determined by the language_code of the event context,
        or 'en' if it is not set.
        """
        session = data['session']
        event_context = data.get('event_context')

        if not await is_user_exist(event_context.chat.id):
            user_locale = event_context.user.language_code or 'en'
            await create_user(event_context.user.id, user_locale, session)

        return await handler(event, data)
