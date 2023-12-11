from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.alias import YesNoCallback


def get_inline_keyboard_game_alias():
    builder = InlineKeyboardBuilder()

    builder.button(text='Yes', callback_data=YesNoCallback(foo='answer', answer='yes'))
    builder.button(text='No', callback_data=YesNoCallback(foo='answer', answer='no'))

    return builder.as_markup()
