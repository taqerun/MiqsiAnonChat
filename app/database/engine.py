from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import DB_URI
from app.core.logs import logger


try:
    engine = create_async_engine(DB_URI, future=True, echo=True)
    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    logger.info("Database engine and session_maker initialized.")
except SQLAlchemyError:
    logger.exception("Error while initializing the database connection.")
    raise
