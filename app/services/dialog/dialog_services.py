from typing import Optional

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey, BaseStorage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logs import logger
from app.database import User, QueueUser, Dialog
from app.services.dialog.dialog_notification_service import DialogNotificationService
from app.states import DialogStates


class DialogService:
    def __init__(
        self,
        bot_id: int,
        session: AsyncSession,
        user: User,
        current_dialog: Optional[Dialog],
        storage: BaseStorage
    ):
        self.bot_id = bot_id
        self.session = session
        self.user = user
        self.current_dialog = current_dialog
        self.notifier = DialogNotificationService()
        self.storage = storage

    def _ctx_key(self, user_id: int) -> StorageKey:
        return StorageKey(bot_id=self.bot_id, user_id=user_id, chat_id=user_id)

    def _get_context(self, user_id: int) -> FSMContext:
        return FSMContext(storage=self.storage, key=self._ctx_key(user_id))

    async def _clear_state(self, user_id: int):
        user_ctx = self._get_context(user_id)
        await user_ctx.clear()

    async def _set_dialog_states(self):
        partner = await self._get_partner()

        if partner:
            user_ctx = self._get_context(self.user.id)
            partner_ctx = self._get_context(partner.id)

            await user_ctx.set_state(DialogStates.dialog)
            await partner_ctx.set_state(DialogStates.dialog)

    async def stop_dialog(self) -> dict[int, Optional[str]]:
        user_ctx = self._get_context(self.user.id)
        before_state = await user_ctx.get_state()

        partner = await self._get_partner()
        partner_id = partner.id if partner else None

        await self._clear_states(partner)
        await self._remove_from_dialog(partner)

        after_state = await user_ctx.get_state()

        return self.notifier.generate(
            before_state=before_state,
            after_state=after_state,
            user=self.user,
            partner_id=partner_id
        )

    @property
    def is_friends(self) -> bool:
        if self.current_dialog:
            return any(str(uid) in self.user.friends for uid in self.current_dialog.users.keys() if uid != self.user.id)
        else:
            return False

    async def start_dialog_search(self) -> dict[int, Optional[str]]:
        user_ctx = self._get_context(self.user.id)
        before_state = await user_ctx.get_state()

        partner_queue = await self._find_partner()

        if not partner_queue:
            await self._enqueue_user()
            await user_ctx.set_state(DialogStates.queue)
            after_state = await user_ctx.get_state()
            return self.notifier.generate(
                before_state=before_state,
                after_state=after_state,
                user=self.user
            )

        partner = await self.session.get(User, partner_queue.id)
        await self._create_dialog(partner)

        partner_ctx = self._get_context(partner.id)

        await user_ctx.set_state(DialogStates.dialog)
        await partner_ctx.set_state(DialogStates.dialog)

        after_state = await user_ctx.get_state()

        return self.notifier.generate(
            before_state=before_state,
            after_state=after_state,
            user=self.user,
            partner_id=partner.id,
            friend_names=await self._get_friend_names(partner)
        )

    async def _get_partner(self) -> Optional[User]:
        if not self.current_dialog:
            return None
        partner_id = self.current_dialog.users.get(str(self.user.id))
        return await self.session.get(User, partner_id) if partner_id else None

    async def _clear_states(self, partner: Optional[User]):
        await self._clear_state(self.user.id)
        if partner:
            await self._clear_state(partner.id)

    async def _remove_from_dialog(self, partner: Optional[User]):
        if partner:
            self.user.dialog_partner_id = None
            partner.dialog_partner_id = None
        if self.current_dialog:
            await self.session.delete(self.current_dialog)
        if self.user.queue_entry:
            await self.session.delete(self.user.queue_entry)
        await self.session.commit()

    async def _find_partner(self) -> Optional[QueueUser]:
        query = (
            select(QueueUser)
            .where(QueueUser.id != self.user.id)
            .where(QueueUser.locale == self.user.locale)
            .where(QueueUser.mode == self.user.mode)
            .with_for_update(skip_locked=True)
        )
        if self.user.interests:
            query = query.where(QueueUser.interests.op('&&')(self.user.interests))
        return await self.session.scalar(query)

    async def _enqueue_user(self):
        if not self.user.queue_entry:
            queue_entry = QueueUser(
                id=self.user.id,
                locale=self.user.locale,
                interests=self.user.interests,
                mode=self.user.mode
            )
            self.user.queue_entry = queue_entry
            self.session.add(queue_entry)
            logger.info("User %s added to queue", self.user.id)
        await self.session.commit()

    async def _create_dialog(self, partner: User):
        await self.session.delete(partner.queue_entry)
        dialog = Dialog(
            users={self.user.id: partner.id, partner.id: self.user.id},
            mode=self.user.mode,
            settings={}
        )
        self.user.dialog_partner_id = partner.id
        partner.dialog_partner_id = self.user.id

        self.current_dialog = dialog
        self.session.add(dialog)
        logger.info("Dialog started: %s <=> %s", self.user.id, partner.id)
        await self.session.commit()

    async def _get_friend_names(self, partner: User) -> dict:
        result = {}
        if partner and str(partner.id) in self.user.friends:
            result[self.user.id] = self.user.friends[str(partner.id)]['name']
        if str(self.user.id) in partner.friends:
            result[partner.id] = partner.friends[str(self.user.id)]['name']
        return result
