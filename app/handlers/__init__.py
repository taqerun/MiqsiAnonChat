from .start import start_router
from app.handlers.dialog.friend import friend_router
from .settings.mode import mode_router
from .settings.interests import interests_router
from .settings.language import language_router
from .settings.friends import friends_settings_router
from .dialog.search import search_router
from .dialog.stop import stop_router
from .dialog.chat import chat_router
from .dialog.next import next_router


all_routers = [
    friend_router,
    start_router,
    language_router,
    search_router,
    interests_router,
    stop_router,
    next_router,
    mode_router,
    friends_settings_router,
    chat_router # всегда должен загружаться в последнюю очередь
]
