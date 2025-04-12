from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.database.models import User


class DatabaseMiddleware(BaseMiddleware):
    """
    Middleware that injects the SQLAlchemy session, user instance, and dialog
    into the handler's data dictionary.
    """

    def __init__(self, session_pool: async_sessionmaker) -> None:
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        event_context = data.get('event_context')

        async with self.session_pool() as session:
            data['session'] = session
            data['user'] = await session.get(User, event_context.chat.id)

            return await handler(event, data)
