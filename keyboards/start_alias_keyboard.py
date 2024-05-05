from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.alias import StartCallback


def get_inline_keyboard_start_alias():
    """
    Generuje klávesnici pro hru Alias.

    Returns:
        InlineKeyboardMarkup: Klávesnice pro začátek a konec hry.
    """
    builder = InlineKeyboardBuilder()

    builder.button(text='Start', callback_data=StartCallback(foo='start'))
    builder.button(text='End game', callback_data=StartCallback(foo='end'))
    return builder.as_markup()
