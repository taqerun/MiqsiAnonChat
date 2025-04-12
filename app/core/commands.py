from typing import Callable, Dict, List, Union

from aiogram import Router, F
from aiogram.filters import Filter, Command, StateFilter
from aiogram.types import BotCommand, Message, TelegramObject

from app.core.config import i18n
from app.utils import get_available_locales


# Dictionary to hold registered bot commands and their descriptions
_registered_commands: Dict[str, str] = {}


def register_command(command: str, description: str) -> Callable:
    """
    Decorator to register a bot command with its description.

    Args:
        command (str): Command without leading slash (e.g. "start").
        description (str): Description shown in Telegram menu.

    Returns:
        Callable: The wrapped function.
    """
    def decorator(func: Callable) -> Callable:
        _registered_commands[command] = description
        return func

    return decorator


def get_registered_commands() -> List[BotCommand]:
    """
    Get all registered bot commands for setting them via set_my_commands().

    Returns:
        List[BotCommand]: List of aiogram command objects.
    """
    return [BotCommand(command=cmd, description=desc) for cmd, desc in _registered_commands.items()]


def register_localized_commands(
    router: Router,
    commands: str,
    *filters: Filter
) -> Callable[[Callable[[Message], None]], Callable[[Message], None]]:
    """
    Decorator to register message handlers for localized command texts.

    Args:
        router (Router): Aiogram router to attach the handlers to.
        commands (Union[str, List[str]]): One or more localized command strings.

    Returns:
        Callable: Decorator to wrap handler function.
    """
    available_locales = get_available_locales()

    def decorator(handler: Callable[[Message], None]) -> Callable[[Message], None]:
        for locale in available_locales:
            localized_text = i18n.gettext(commands, locale=locale)
            router.message(F.text == localized_text, *filters)(handler)

        return handler

    return decorator


def setup_command(router: Router, command: str, reply_command: str, *filters: Filter):
    def decorator(handler: Callable[[TelegramObject], None]):
        router.message(Command(command))(handler)
        register_localized_commands(router, reply_command, *filters)(handler)
        register_command(command, reply_command)(handler)

        return handler

    return decorator
