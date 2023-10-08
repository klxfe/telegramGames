from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from keyboards.games_keyboard import get_keyboard_games_car
from texts.buttons import text_go_to_menu
main_router = Router(name=__name__)


@main_router.message(F.text == text_go_to_menu)
@main_router.message(CommandStart())
async def message_start_handler(message: Message):
    await message.answer('Main menu:\nChoose the option.', reply_markup=get_keyboard_games_car())




