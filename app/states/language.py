from aiogram.fsm.state import StatesGroup, State


class LanguageStates(StatesGroup):
    choosing_language = State()
