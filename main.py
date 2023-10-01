import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, ChatMemberUpdatedFilter, IS_MEMBER
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.types.chat_member_updated import ChatMemberUpdated
from handlers.main_handlers import main_router
from handlers.guess_the_word_handlers import guess_the_word_router


TOKEN = '5999510344:AAEZmlkYzi4HeiJW7wisjyEoA_BHINaR-eQ'




async def main() -> None:
    dp = Dispatcher()
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    dp.include_routers(
        main_router,
        guess_the_word_router,
    )
    await dp.start_polling(bot)

    # allowed_updated = dp.resolve_used_update_types()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
