from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.i18n import gettext as _

from app.database import User


class UserFriendsService:
    def __init__(self, user: User, session: AsyncSession):
        """
        :param user:
        :param session:
        """
        self.user = user
        self.session = session

    def get_friend_id_by_name(self, name: str) -> int | None:
        for friend_id, friend_data in self.user.friends.items():
            if friend_data['name'] == name:
                return int(friend_id)

    def get_friend_name(self, name: str) -> Optional[str]:
        """
        Get the name of a friend by their ID.

        :param name: Name of the friend.
        :return: Friend's name if found, otherwise None.
        """
        friend_id = self.get_friend_id_by_name(name)

        if friend_id:
            return self.user.friends.get(str(friend_id), {}).get('name')

    async def rename(self, name: str, new_name: str) -> dict[int, str]:
        """
        Rename a friend in the user's friend list.

        :return: A dictionary with a localized message about the result.
        """
        friend_key = str(self.get_friend_id_by_name(name))

        if friend_key in self.user.friends:
            old_name = self.user.friends[friend_key]['name']
            self.user.friends[friend_key]['name'] = new_name.capitalize()
            await self.session.commit()
            return {
                self.user.id: _('<b>Friend with name <code>{old_name}</code> renamed to <code>{new_name}</code></b>')
                .format(old_name=old_name, new_name=new_name)
            }

        return {'message': _('<b>❌ Friend is not found</b>')}

    async def delete(self, name: str) -> dict[int, str]:
        """
        Deletes a friend by ID.

        :param name: Name of friend's user.
        :return: Dict with success or error message.
        """
        friend_id = self.get_friend_id_by_name(name)
        friend_key = str(friend_id)

        if friend_key in self.user.friends:
            friend_name = self.user.friends[friend_key]['name']
            friend = await self.session.get(User, friend_id)
            name_in_friend_friends = friend.friends[str(self.user.id)]['name']

            del friend.friends[str(self.user.id)]
            del self.user.friends[friend_key]

            await self.session.commit()

            return {
                self.user.id: _('<b>✅ <code>{name}</code> has been removed from friends</b>')
                .format(name=friend_name),
                int(friend.id): _('<b><code>{name}</code> has removed you from friends</b>')
                .format(name=name_in_friend_friends)
            }

        return {self.user.id: _('<b>❌ Friend is not found</b>')}
