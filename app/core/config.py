import os
from pathlib import Path
from aiogram.utils.i18n import I18n
from redis.asyncio import Redis

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# === Lazy-load конфигурации ===

def get_bot_token() -> str:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ BOT_TOKEN is missing.")
    return token

def get_db_uri() -> str:
    uri = os.getenv("DB_URI")
    if not uri:
        raise RuntimeError("❌ DB_URI is missing.")
    return uri

def get_redis_url() -> str:
    return os.getenv("REDIS_HOST", "redis://localhost:6379")

# === Внешние сервисы ===
redis = Redis.from_url(get_redis_url(), decode_responses=True)

# === Локализация ===
i18n = I18n(
    path=BASE_DIR / "locales",
    default_locale="en",
    domain="messages",
)
