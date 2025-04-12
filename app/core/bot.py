from typing import Sequence

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from app.core import commands, logs
from app.core.config import BOT_TOKEN, redis, i18n
from app.database import session_maker
from app.handlers import all_routers
from app.middlewares import DatabaseMiddleware, MyI18nMiddleware, ChecksMiddleware
from app.middlewares.dialog import DialogMiddleware
from app.middlewares.user_friends_services import UserFriendsServicesMiddleware
from app.middlewares.utils_services import UtilsServicesMiddleware

dp = Dispatcher(storage=RedisStorage(redis=redis))


async def setup_middlewares() -> None:
    """
    Configure all middlewares for the bot dispatcher.
    """
    dp.update.middleware(DatabaseMiddleware(session_pool=session_maker))
    dp.update.middleware(ChecksMiddleware())
    dp.update.middleware(MyI18nMiddleware(i18n=i18n))
    dp.update.middleware(UtilsServicesMiddleware())
    dp.update.middleware(DialogMiddleware())
    dp.update.middleware(UserFriendsServicesMiddleware())


async def setup_routers(routers: Sequence[Router]) -> None:
    """
    Register all provided routers to the dispatcher.

    Args:
        routers (Sequence[Router]): List of routers to include.
    """
    for router in routers:
        try:
            dp.include_router(router)
            logs.logger.info(f"✅ Router [{router.name}] successfully connected.")
        except Exception as e:
            logs.logger.error(f"❌ Router [{router.name}] failed to connect: {e}")


async def start_bot() -> None:
    """
    Main bot startup logic: configure bot, middleware, routers, and start polling.
    """
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_my_commands(commands.get_registered_commands())

        await setup_middlewares()
        await setup_routers(all_routers)

        logs.logger.info("🚀 Bot is starting...")
        await dp.start_polling(bot)

    except Exception as e:
        logs.logger.critical(f"🔥 Failed to start the bot: {e}")

    finally:
        await shutdown_bot(bot)


async def shutdown_bot(bot: Bot) -> None:
    """
    Gracefully close bot connection and clean up.
    """
    await bot.session.close()
    logs.logger.info("🛑 Bot has been stopped.")
