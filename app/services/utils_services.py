from aiogram import Bot


class UtilsServices:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_messages(self, data: dict, keyboard=None):
        for user_id, user_message in data.items():
            if user_message:
                await self.bot.send_message(user_id, user_message, reply_markup=keyboard)
