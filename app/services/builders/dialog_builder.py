from aiogram import Bot
from aiogram.fsm.storage.base import BaseStorage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import User, Dialog
from app.services.dialog.dialog_services import DialogService


class DialogContext:
    def __init__(self, service: DialogService, partner: User):
        self.service = service
        self.user = service.user
        self.partner = partner


class DialogBuilder:
    @staticmethod
    async def build(session: AsyncSession, user_id: int, bot: Bot, storage: BaseStorage) -> DialogContext:
        user = await session.scalar(select(User).options(selectinload(User.queue_entry)).where(User.id == user_id))
        partner = None

        if not user:
            raise ValueError(f"User {user_id} not found")

        current_dialog = await session.scalar(
            select(Dialog).where(Dialog.users.has_key(str(user_id)))
        )

        if current_dialog:
            partner = await session.get(User, current_dialog.users[str(user.id)])

        service = DialogService(
            bot_id=bot.id,
            storage=storage,
            user=user,
            session=session,
            current_dialog=current_dialog
        )

        return DialogContext(service=service, partner=partner)
