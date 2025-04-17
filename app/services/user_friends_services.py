from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext

from app.states import FriendsStates
from app.database import User
from app.utils import HTML


class UserFriendsService:
    def __init__(self, user: User, session: AsyncSession, state: FSMContext):
        """
        :param user:
        :param session:
        """
        self.user = user
        self.session = session
        self.state = state

    def get_friend_id_by_name(self, name: str) -> int | None:
        for friend_id, friend_data in self.user.friends.items():
            if friend_data['name'] == name:
                return int(friend_id)


    def get_friend_name(self, name: str, **kwargs) -> Optional[str]:
        """
        Get the name of a friend by their ID.

        :param name: Name of the friend.
        :return: Friend's name if found, otherwise None.
        """
        friend_id = self.get_friend_id_by_name(name)

        if friend_id:
            return self.user.friends.get(str(friend_id), {}).get('name')

    async def rename(self, name: str) -> dict[int, str]:
        """
        Rename a friend in the user's friend list.

        :return: A dictionary with a localized message about the result.
        """
        friend_key = str(self.get_friend_id_by_name(name))
        state_data = await self.state.get_data()
        new_name = state_data.get('new_name')

        if not new_name:
            await self.state.update_data(name=name)
            await self.state.set_state(FriendsStates.rename)
            return {self.user.id: HTML.b(_('Enter new name for friend: {name}').format(name=name))}
        
        elif new_name.lower() == name.lower():
            return {self.user.id: '❌ ' + HTML.b(_('Choose difirent name'))}

        elif friend_key in self.user.friends.keys():
            self.user.friends[friend_key]['name'] = new_name.capitalize()
            flag_modified(self.user, "friends")
            await self.session.commit()
            await self.state.clear()
            return {
                self.user.id: HTML.b(_('Friend with name {old_name} renamed to {new_name}'))
                .format(old_name=HTML.code(name), new_name=HTML.code(new_name))
            }

        return {self.user.id: '❌ ' + HTML.b(_('Friend is not found'))}

    async def delete(self, name: str) -> dict[int, str]:
        """
        Deletes a friend by name.

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
                self.user.id: '✅ ' + HTML.b(_('{name} has been removed from friends</b>'))
                .format(name=HTML.code(friend_name)),
                int(friend.id): HTML.b(_('{name} has removed you from friends'))
                .format(name=name_in_friend_friends)
            }

        return {self.user.id: '❌ ' + HTML.b(_('Friend is not found'))}
