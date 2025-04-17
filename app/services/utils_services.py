from aiogram import Bot
from aiogram.types import Message


class UtilsServices:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_messages(
            self,
            data: dict,
            keyboard=None,
            edit: bool = False,
            message_for_edit: dict=None,
            keyboards: dict=None
        ):
        for user_id, user_message in data.items():
            if user_message:
                keyboard = keyboard if not keyboards else keyboards[user_id]

                if edit and message_for_edit and message_for_edit['uid'] == user_id:
                    await self.bot.edit_message_text(
                        chat_id=user_id,
                        message_id=message_for_edit['mid'],
                        text=user_message,
                        reply_markup=keyboard
                    )
                else:
                    await self.bot.send_message(user_id, user_message, reply_markup=keyboard)
