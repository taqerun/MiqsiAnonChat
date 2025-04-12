from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import redis
from app.database import User


async def is_user_exist(user_id: int) -> bool:
    """
    Checks if a user exists in the cache.

    Args:
        user_id (int): Telegram user ID.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    
    result: bytes | None = await redis.get(name=str(user_id))

    if not result:
        await redis.set(name=str(user_id), value=b'1')
        return False
    else:
        return True


async def create_user(
    user_id: int,
    locale: str,
    session: AsyncSession,
) -> None:
    """
    Creates a new user in the database.

    Args:
        user_id (int): Telegram user ID.
        locale (str): User's preferred locale.
        session (AsyncSession): SQLAlchemy session.

    Returns:
        None
    """

    user = User(id=user_id, locale=locale)
    session.add(user)

    await session.commit()
