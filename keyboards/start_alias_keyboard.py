from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from callbacks.alias import StartCallback


def get_inline_keyboard_start_alias():
    builder = InlineKeyboardBuilder()

    builder.button(text='Start', callback_data=StartCallback(foo='start'))
    builder.button(text='End game', callback_data=StartCallback(foo='end'))
    return builder.as_markup()
