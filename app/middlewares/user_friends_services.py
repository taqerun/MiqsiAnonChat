from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.services.user_friends_services import UserFriendsService


class UserFriendsServicesMiddleware(BaseMiddleware):
    """
    Middleware that injects DialogContext (dialog_ctx) into handler data,
    based on current user and FSM state. Works with both messages and callbacks.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session = data['session']
        data['friends_service'] = UserFriendsService(data['user'], session)

        return await handler(event, data)
