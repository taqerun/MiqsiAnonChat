from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import redis
from app.database import User


async def is_user_exist(user_id) -> bool:
    result = await redis.get(name=str(user_id))

    if not result:
        await redis.set(name=str(user_id), value=1)
        return False
    else:
        return True


async def create_user(user_id: int, locale: str, session: AsyncSession) -> None:
        user = User(id=user_id, locale=locale)
        session.add(user)

        await session.commit()
