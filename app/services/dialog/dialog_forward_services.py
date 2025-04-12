from aiogram import Bot, types
from redis.asyncio import Redis
from app.core import logs
from aiogram.utils.i18n import gettext as _


class DialogForwardService:
    def __init__(self, bot: Bot, redis: Redis, dialog_id: int):
        """
        :param bot:
        :param redis:
        :param dialog_id:
        """
        self.bot = bot
        self.redis = redis
        self.dialog_id = dialog_id

    async def get_message_target_id(self, message: types.Message) -> int | None:
        """
        :param message:
        :return:
        """
        if message:
            redis_key = f'{self.dialog_id}:{message.message_id}'
            await message.answer(redis_key)
            reply_id = await self.redis.get(redis_key)

            return int(reply_id) if reply_id else None

    async def edit_message(self, original_message: types.Message):
        forwarded_id = await self.get_message_target_id(original_message)

        try:
            if forwarded_id:
                await original_message.answer(f'{forwarded_id}')
                await original_message.bot.edit_message_text(
                    chat_id=original_message.chat.id,
                    message_id=forwarded_id,
                    text=original_message.text,
                    reply_markup=original_message.reply_markup
                )
            else:
                await original_message.answer('What?')

        except Exception as e:
            logs.logger.exception("❌ Failed to edit forwarded message", exc_info=e)


    async def forward(self, message: types.Message, recipient_id: int) -> int | None:
        """
        :param message:
        :param recipient_id:
        :return:
        """
        try:
            reply_to_id = await self.get_message_target_id(message.reply_to_message)
            forwarded = await self.bot.copy_message(
                chat_id=recipient_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=message.reply_markup,
                protect_content=message.has_protected_content,
                caption=message.caption,
                caption_entities=message.caption_entities,
                allow_sending_without_reply=True,
                reply_to_message_id=reply_to_id
            )

            await self.redis.set(
                f"{self.dialog_id}:{forwarded.message_id}",
                message.message_id,
                ex=3600
            )
            await self.redis.set(
                f"{self.dialog_id}:{message.message_id}",
                forwarded.message_id,
                ex=3600
            )

            return forwarded.message_id

        except Exception as e:
            logs.logger.exception("❌ Failed to forward message to dialog partner", exc_info=e)
            await message.reply(_("❌ Failed to deliver message. The user may have blocked the bot."))
