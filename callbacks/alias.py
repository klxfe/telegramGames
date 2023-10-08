from aiogram.filters.callback_data import CallbackData


class StartCallback(CallbackData, prefix="start"):
    foo: str


class YesNoCallback(CallbackData, prefix="yesno"):
    foo: str
    answer: str
