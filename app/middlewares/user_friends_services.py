from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.services.user_friends_services import UserFriendsService


class UserFriendsServicesMiddleware(BaseMiddleware):
    """
    Middleware that injects UserFriendsService (friends_service) into handler data.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session = data.get('session')
        user = data.get('user')
        state = data.get('state')

        data['friends_service'] = UserFriendsService(user, session, state)

        return await handler(event, data)
