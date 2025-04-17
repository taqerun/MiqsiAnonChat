from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.services.utils_services import UtilsServices


class UtilsServicesMiddleware(BaseMiddleware):
    """
    Middleware that injects UtilsServices instance into handler data,
    allowing utilities to be easily accessed in handlers.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        bot = data.get('bot')
        if not bot:
            raise ValueError("Bot instance not found in data")

        data['utils_service'] = UtilsServices(bot)

        return await handler(event, data)
