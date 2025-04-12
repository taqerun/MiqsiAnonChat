from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.services.utils_services import UtilsServices


class UtilsServicesMiddleware(BaseMiddleware):
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
        bot = data['bot']

        data['utils_service'] = UtilsServices(bot)

        return await handler(event, data)
