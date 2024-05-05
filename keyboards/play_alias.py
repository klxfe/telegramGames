from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from callbacks.alias import YesNoCallback


def get_inline_keyboard_game_alias():
    """
    Generuje inline klávesnici pro hru Alias s odpověděmi Ano/Ne

    Returns:
        InlineKeyboardMarkup: Inline klávesnice pro hru
    """
    builder = InlineKeyboardBuilder()

    builder.button(text='Yes', callback_data=YesNoCallback(foo='answer', answer='yes'))
    builder.button(text='No', callback_data=YesNoCallback(foo='answer', answer='no'))

    return builder.as_markup()
