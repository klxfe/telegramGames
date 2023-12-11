import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from handlers.codenames_handler import codenames_router
from handlers.main_handlers import main_router
from handlers.guess_the_word_handlers import guess_the_word_router
from handlers.alias_handler import alias_router
with open('bot_token.txt') as file:
    TOKEN = file.read()




async def main() -> None:
    dp = Dispatcher()
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    dp.include_routers(
        main_router,
        guess_the_word_router,
        alias_router,
        codenames_router,
    )
    await dp.start_polling(bot)

    # allowed_updated = dp.resolve_used_update_types()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
