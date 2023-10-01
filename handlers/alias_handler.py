import asyncio
import random
from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message

from keyboards.games_keyboard import get_keyboard_games_car
from texts.buttons import text_play_alias
from database import register_guess_new_game, register_user_new_game, drop_game, check_available_game, get_game_users, \
    get_guess_full_word, give_user_score, get_guessed_part_word, set_guessed_part_word
from constants import seconds_helper, seconds_to_start

alias_router = Router(name=__name__)


@alias_router.message(F.text == text_play_alias)
async def message_alias_handler(message: Message):
    if check_available_game():
        await message.answer('Some games are in cache.\nType /end to end all games and try one more time')
        return