from os import getenv
from pathlib import Path

from aiogram.utils.i18n import I18n
from dotenv import load_dotenv
from redis.asyncio import Redis


# === Load environment variables ===
load_dotenv()

# === Paths ===
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

# === Environment configuration ===
BOT_TOKEN: str | None = getenv('BOT_TOKEN')
DB_URI: str | None = getenv('DB_URI')
REDIS_URL: str | None = getenv('REDIS_URL')

if not BOT_TOKEN:
    raise RuntimeError('❌ Environment variable BOT_TOKEN is missing.')
if not DB_URI:
    raise RuntimeError('❌ Environment variable DB_URI is missing.')

# === External services ===
redis: Redis = Redis.from_url(REDIS_URL)

# === Internationalization ===
i18n: I18n = I18n(
    path=BASE_DIR / "locales",
    default_locale="en",
    domain="messages",
)
