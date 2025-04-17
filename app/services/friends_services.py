from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.i18n import gettext as _

from app.database import User
from app.utils import HTML


class FriendsService:
    def __init__(self, user1: User, user2: User, session: AsyncSession) -> dict:
        """
        :param user1:
        :param user2:
        :param session:
        """
        self.user1 = user1
        self.user2 = user2
        self.session = session

    @property
    def is_friends(self) -> bool:
        """
        Check if the users are already friends.

        :return: True if both users have each other in their friend lists.
        """
        return (
            str(self.user1.id) in self.user2.friends and
            str(self.user2.id) in self.user1.friends
        )

    async def make_friends(self) -> dict[int, str]:
        """
        Create a friendship between two users if they are not already friends.

        :return: A dictionary mapping user IDs to localized messages about the friendship status.
        """
        user1_name = f'Friend {len(self.user1.friends) + 1}'
        user2_name = f'Friend {len(self.user2.friends) + 1}'

        self.user1.friends[str(self.user2.id)] = {'name': user1_name}
        self.user2.friends[str(self.user1.id)] = {'name': user2_name}

        await self.session.commit()

        text_template = HTML.b(_(
            'You now have an anonymous friend {name}!\n\n'
            'You can submit a request to communicate with '
            'your friends in the main menu of the bot'
        ))

        return {
            self.user1.id: text_template.format(name=HTML.code(user1_name)),
            self.user2.id: text_template.format(name=HTML.code(user2_name)),
        }
