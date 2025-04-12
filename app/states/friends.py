from aiogram.fsm.state import StatesGroup, State


class FriendsStates(StatesGroup):
    request = State()
    rename = State()
