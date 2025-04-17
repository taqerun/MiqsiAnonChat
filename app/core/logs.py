import logging
from logging.handlers import RotatingFileHandler
from os import getenv
from pathlib import Path

from app.core.config import BASE_DIR

# === Constants ===
LOG_LEVEL: str = getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT: str = (
    "[%(asctime)s] [%(levelname)-4s] "
    "[%(name)s.%(funcName)s:%(lineno)d] - %(message)s"
)


# === Paths ===
LOGS_DIR: Path = BASE_DIR / "logs"
LOG_FILE: Path = LOGS_DIR / "app.log"

# Ensure log directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# === Formatters ===
formatter = logging.Formatter(LOG_FORMAT)

# === Handlers ===

# File handler with rotation
file_handler = RotatingFileHandler(
    filename=LOG_FILE,
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=3,
    encoding="utf-8"
)
file_handler.setFormatter(formatter)

# Console (stdout) handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# === Root Logger Configuration ===
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    handlers=[file_handler, console_handler],
)

# === Logger Instance ===
logger = logging.getLogger(__name__)
logger.info("✅ Logger initialized successfully.")
