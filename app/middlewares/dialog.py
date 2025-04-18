from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.services.builders.dialog_builder import DialogBuilder


class DialogMiddleware(BaseMiddleware):
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
        event_context = data.get('event_context')
        user_id = event_context.user.id
        bot = data.get('bot')
        session = data.get('session')


        data['dialog_ctx'] = await DialogBuilder.build(
            session=session,
            user_id=user_id,
            bot=bot,
            storage=data['state'].storage,
        )

        return await handler(event, data)
