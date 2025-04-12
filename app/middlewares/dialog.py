from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message

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
        message: Message | None = getattr(event, 'message', None)
        callback: CallbackQuery | None = getattr(event, 'callback_query', None)

        user = (message or callback).from_user
        user_id = user.id
        bot = data['bot']
        session = data['session']

        data['dialog_ctx'] = await DialogBuilder.build(
            session=session,
            user_id=user_id,
            bot=bot,
            storage=data['state'].storage,
        )

        return await handler(event, data)
