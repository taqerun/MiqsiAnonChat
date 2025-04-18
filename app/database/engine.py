from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_db_uri
from app.core.logs import logger


try:
    logger.info("Initializing database engine and session_maker...")
    engine = create_async_engine(get_db_uri(), future=True, echo=True)
    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    logger.info("Database connection established.")
    logger.info("Database engine and session_maker initialized.")
except SQLAlchemyError:
    logger.exception("Error while initializing the database engine and session_maker.")
    raise
