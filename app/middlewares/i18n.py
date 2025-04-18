from typing import Dict, Any

from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18nMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


class MyI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        session: AsyncSession = data.get('session')
        event_context = data.get('event_context')

        if event_context and session:
            result = await session.execute(select(User.locale).where(User.id == event_context.user.id))
            user_locale = result.scalar_one_or_none()
            if user_locale:
                return user_locale

        return "en"
