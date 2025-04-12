from aiogram.fsm.state import StatesGroup, State

class DialogStates(StatesGroup):
    dialog = State()
    friend_request = State()
    queue = State()
