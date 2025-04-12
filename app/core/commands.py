from typing import Callable, Dict, List

from aiogram import Router, F
from aiogram.filters import Filter, Command
from aiogram.types import BotCommand, Message

from app.core.config import i18n
from app.utils import get_available_locales


# Dictionary to hold registered bot commands and their descriptions
_registered_commands: Dict[str, str] = {}


def register_command(command: str, description: str) -> Callable[[Callable], Callable]:
    """
    Registers a command and its description in the global dictionary of
    registered commands.

    Args:
        command (str): The command to register.
        description (str): The description of the command.

    Returns:
        Callable[[Callable], Callable]: A decorator that will register the command
            in the global dictionary of registered commands.
    """
    def decorator(func: Callable) -> Callable:
        """
        Registers the command in the global dictionary of registered commands.

        Args:
            func (Callable): The function to register the command on.

        Returns:
            Callable: The registered function.
        """
        _registered_commands[command] = description
        return func

    return decorator


def get_registered_commands() -> List[BotCommand]:
    """
    Returns a list of registered bot commands and their descriptions.

    The list is populated by the @register_command decorator, which is used to
    register a command and its description. The description is used to populate
    the description field of the BotCommand object.

    Returns:
        List[BotCommand]: A list of BotCommand objects, each containing the
            command name and its description.
    """
    return [BotCommand(command=cmd, description=desc) for cmd, desc in _registered_commands.items()]


def register_localized_commands(
    router: Router,
    commands: str,
    *filters: Filter
) -> Callable[[Callable[[Message], None]], Callable[[Message], None]]:
    available_locales = get_available_locales()

    def decorator(handler: Callable[[Message], None]) -> Callable[[Message], None]:
        """
        Register a message handler for a given command and its localized version.

        Args:
            commands (str): The command to register the handler on.
            filters (Filter): Additional filters to apply to the message handler.

        The handler will be registered for each localized version of the command
        in the available locales.
        """
        # Iterate over the available locales and register the handler for each localized command
        for locale in available_locales:
            # Get the localized text for the command in the current locale
            localized_text = i18n.gettext(commands, locale=locale)
            # Register the handler with the router using the localized command
            router.message(F.text == localized_text, *filters)(handler)

        # Return the decorated handler
        return handler

    return decorator


def setup_command(router: Router, command: str, reply_command: str, *filters: Filter):
    def decorator(handler: Callable[[Message], None]) -> Callable[[Message], None]:
        """
        Register a message handler for a given command and its localized version.

        Args:
            handler (Callable[[Message], None]): The message handler function.
        
        Returns:
            Callable[[Message], None]: The decorated handler.
        """
        router.message(Command(command))(handler)
        register_localized_commands(router, reply_command, *filters)(handler)
        register_command(command, reply_command)(handler)

        return handler

    return decorator
