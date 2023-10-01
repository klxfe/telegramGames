from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from texts.buttons import text_play_alias, text_play_guess_the_word, text_go_to_menu

def get_keyboard_games_car():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=text_play_guess_the_word), KeyboardButton(text=text_play_alias))
    builder.add(KeyboardButton(text=text_go_to_menu))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)