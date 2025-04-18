from os import getenv
from pathlib import Path

from aiogram.utils.i18n import I18n
from dotenv import load_dotenv
from redis.asyncio import Redis


# === Load environment variables ===
load_dotenv

# === Paths ===
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

# === Environment configuration ===
DB_URI: str | None = getenv('DB_URI')
REDIS_URL: str | None = getenv('REDIS_HOST')

@property
def get_bot_token():
    token = getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ BOT_TOKEN is missing.")
    return token


if not DB_URI:
    raise RuntimeError('❌ Environment variable DB_URI is missing.')

# === External services ===
redis: Redis = Redis(host=REDIS_URL, decode_responses=True)

# === Internationalization ===
i18n: I18n = I18n(
    path=BASE_DIR / "locales",
    default_locale="en",
    domain="messages",
)
