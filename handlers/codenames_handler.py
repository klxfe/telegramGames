import json
import random
from prettytable import PrettyTable

from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from database import register_new_codenames_game, join_blue_codenames, join_red_codenames, info_codenames, \
    leave_codenames, join_red_capitan, join_blue_capitan, start_codenames_game, get_codenames_all_words, \
    get_codenames_red_words, get_codenames_opened_words, get_codenames_blue_words, get_codenames_red_cap_id, \
    get_codenames_blue_cap_id, get_codenames_black_word, set_codenames_current_team, get_codenames_current_team, \
    set_codenames_tries_red, set_codenames_tries_blue, get_codenames_tries_red, set_codenames_opened_word, \
    get_codenames_tries_blue, get_codenames_blue_team_ids, get_codenames_red_team_ids, drop_codenames_game
from texts.buttons import text_play_codenames

codenames_router = Router(name=__name__)

RED_HEART_EMOJI = '❤️'
BLUE_HEART_EMOJI = '💙'
BLACK_HEART_EMOJI = '🖤'
WHITE_HEART_EMOJI = '🤍'
DONE_EMOJI = '✅'


def list_contains_elements_of_list(list1, list2):
    """Vratí true, když list1 obsahuje všechny elementy list2, jinak false"""
    return all(element in list1 for element in list2)


def generate_lists_for_game():
    """
    Generuje seznam slov pro hru Codenames.

    Returns:
        tuple: Tuple s celkovým seznameem slov, seznamem červených slov, modrých, a černé slovo.
    """
    with open('sources/codenames.json', encoding="utf-8") as f:
        all_words = json.load(f)
    words = []
    for i in range(25):
        word = random.choice(all_words)
        all_words.remove(word)
        words.append(word)
    words_tmp = words.copy()
    words_red = []

    red_words_count = random.randint(8, 9)
    blue_words_count = 17 - red_words_count
    for i in range(red_words_count):
        word = random.choice(words_tmp)
        words_tmp.remove(word)
        words_red.append(word)
    words_blue = []
    for i in range(blue_words_count):
        word = random.choice(words_tmp)
        words_tmp.remove(word)
        words_blue.append(word)
    word_black = random.choice(words_tmp)
    words = ' '.join(words)
    words_red = ' '.join(words_red)
    words_blue = ' '.join(words_blue)
    return words, words_red, words_blue, word_black


def create_codenames_table_for_chat(chat_id):
    """
      Generuje tabulku slov pro hru Codenames pro konkretní chat.

      Args:
          chat_id: Id chatu

      Returns:
          str: Tabulka se slovy pro hru Codenames.
      """
    all_words: list = get_codenames_all_words(chat_id)
    red_words: list = get_codenames_red_words(chat_id)
    blue_words: list = get_codenames_blue_words(chat_id)
    opened_words: list = get_codenames_opened_words(chat_id)

    table = PrettyTable()
    line = []
    count = 0

    for word in all_words:
        if word in opened_words and word in blue_words:
            line.append(f'{word}{BLUE_HEART_EMOJI}')
        elif word in opened_words and word in red_words:
            line.append(f'{word}{RED_HEART_EMOJI}')
        else:
            line.append(f'{word}')
        count += 1
        if count % 5 == 0:
            table.add_row(line)
            line = []
    result = table.get_string(header=False)
    return result


def create_codenames_table_for_capitan(chat_id):
    """
    Generuje  tabulku se slovy pro hru Codenames pro kapitány týmu v konkretním chatu.

    Args:
        chat_id: Id chatu

    Returns:
        str: Tabulka se slovy pro kapitána pro hru Codenames.
    """
    all_words: list = get_codenames_all_words(chat_id)
    blue_words: list = get_codenames_blue_words(chat_id)
    red_words: list = get_codenames_red_words(chat_id)
    black_word = get_codenames_black_word(chat_id)
    opened_words: list = get_codenames_opened_words(chat_id)

    table = PrettyTable()
    line = []
    count = 0

    for word in all_words:
        if word in blue_words:
            line.append(f'{word}{BLUE_HEART_EMOJI}')
        elif word in red_words:
            line.append(f'{word}{RED_HEART_EMOJI}')
        elif word == black_word:
            line.append(f'{word}{BLACK_HEART_EMOJI}')
        else:
            line.append(f'{word}')
        count += 1
        if count % 5 == 0:
            table.add_row(line)
            line = []
    result = table.get_string(header=False)
    return result


def create_codenames_table_for_players(chat_id):
    """
        Generuje  tabulku se slovy pro hru Codenames pro hrače týmu v konkretním chatu.

        Args:
            chat_id: Id chatu

        Returns:
            str: Tabulka se slovy pro hru Codenames.
        """

    all_words: list = get_codenames_all_words(chat_id)
    blue_words: list = get_codenames_blue_words(chat_id)
    red_words: list = get_codenames_red_words(chat_id)
    black_word = get_codenames_black_word(chat_id)
    opened_words: list = get_codenames_opened_words(chat_id)

    table = PrettyTable()
    line = []
    count = 0

    for word in all_words:
        if word in opened_words:
            if word in blue_words:
                line.append(f'{word}{BLUE_HEART_EMOJI}')
            elif word in red_words:
                line.append(f'{word}{RED_HEART_EMOJI}')
            elif word == black_word:
                line.append(f'{word}{BLACK_HEART_EMOJI}')
            else:
                line.append(f'{word}{WHITE_HEART_EMOJI}')
        else:
            line.append(f'{word}')
        count += 1
        if count % 5 == 0:
            table.add_row(line)
            line = []
    result = table.get_string(header=False)
    return result


@codenames_router.message(F.text == text_play_codenames)
async def message_codenames_handler(message: Message):
    """
    Obsluha zprávy pro začátek hry Codenames.

    Args:
        message (Message): Objekt zprávy z Telegramu.
    """
    await message.answer('You would like to play codenames.\n'
                         'All games was deleted and new game has statred.'
                         '\nType /join_blue or /join_red to join'
                         '\n/codenames - for info'
                         '\n/leave_codenames = for leave'
                         '\n/blue_cap - to be blue capitan'
                         '\n/red_cap - to be red capitan'
                         '\n/codenames_start -  to start')
    words, words_red, words_blue, word_black = generate_lists_for_game()
    register_new_codenames_game(words_all=words, words_red=words_red, words_blue=words_blue, word_black=word_black,
                                chat_id=message.chat.id)


@codenames_router.message(Command('join_blue'))
async def command_codenames_join_blue_handler(message: Message):
    """
       Obsluha přikazu pro připojení do modrého týmu ve hře Codenames.

       Args:
           message (Message): Objekt zprávy z Telegramu.
       """
    msg_result = join_blue_codenames(chat_id=message.chat.id, user_id=message.from_user.id)
    await message.reply(msg_result)


@codenames_router.message(Command('join_red'))
async def command_codenames_join_red_handler(message: Message):
    """
      Obsluha přikazu pro připojení do červeného týmu ve hře Codenames.

      Args:
          message (Message): message (Message): Objekt zprávy z Telegramu.
      """
    msg_result = join_red_codenames(chat_id=message.chat.id, user_id=message.from_user.id)
    await message.reply(msg_result)


@codenames_router.message(Command('codenames'))
async def command_codenames_info_handler(message: Message):
    """
       Obsluha přikazu pro ziskání aktuálního stavu hry Codenames.

       Args:
           message (Message): Objekt zprávy z Telegramu.
       """
    msg_result = info_codenames(message.chat.id)
    await message.reply(f'users:\n{msg_result}')


@codenames_router.message(Command('leave_codenames'))
async def command_codenames_leave_handler(message: Message):
    """
    Obsluha přikazu pro opuštění hry Codenames.

    Args:
        message (Message): Objekt zprávy z Telegramu.
    """
    msg_result = leave_codenames(chat_id=message.chat.id, user_id=message.from_user.id)
    await message.reply(msg_result)


@codenames_router.message(Command('red_cap'))
async def command_codenames_red_cap_handler(message: Message, bot: Bot):
    """
    Obsluha přikazu pro přihlášení do roli kapitánu červeného týmu.

    Args:
        message (Message): Objekt zprávy z Telegramu.
        bot (Bot): Objekt bota.
    """
    try:
        await bot.send_message(message.from_user.id, 'You now cap of red')
    except:
        await message.answer(f'Capitan should type start in dm bot {await bot.get_me()}')
        return

    join_red_capitan(chat_id=message.chat.id, user_id=message.from_user.id)
    await message.answer('Done. You are cap of red')


@codenames_router.message(Command('blue_cap'))
async def command_codenames_blue_cap_handler(message: Message, bot: Bot):
    """
    Obsluha přikazu pro přihlášení do roli kapitánu modrého týmu.

    Args:
        message (Message): Objekt zprávy z Telegramu.
        bot (Bot): Objekt bota.
    """
    try:
        await bot.send_message(message.from_user.id, 'You now cap of blue')
    except:
        await message.answer(f'Capitan should type start in dm bot {await bot.get_me()}')
        return
    join_blue_capitan(chat_id=message.chat.id, user_id=message.from_user.id)
    await message.answer('Done. You are cap of blue')


@codenames_router.message(Command('codenames_start'))
async def command_codenames_start_handler(message: Message, bot: Bot):
    """
    Obsluha přikazu pro začátek hry Codenames.

    Args:
        message (Message): Objekt zprávy z Telegramu.
        bot (Bot): Objekt bota.
    """
    res = start_codenames_game(chat_id=message.chat.id)
    blue_words: list = get_codenames_blue_words(message.chat.id)
    red_words: list = get_codenames_red_words(message.chat.id)
    if not res:
        await message.answer('Something went wrong. /codenames - info about game')
        return
    red_id = get_codenames_red_cap_id(message.chat.id)
    blue_id = get_codenames_blue_cap_id(message.chat.id)
    try:
        await bot.send_message(red_id, create_codenames_table_for_capitan(message.chat.id))
        await bot.send_message(blue_id, create_codenames_table_for_capitan(message.chat.id))
        await message.answer(create_codenames_table_for_players(message.chat.id))
    except:
        await message.answer('Something went wrong')
        return

    if len(blue_words) > len(red_words):
        await message.answer(
            'Done. Game has started\nCaps received words\nBlue team starts\nCap - /hint phrase [num. words]\n/cndend '
            '- to stop game')
        set_codenames_current_team(message.chat.id, 'blue')
        return

    if len(red_words) > len(blue_words):
        await message.answer(
            'Done. Game has started\nCaps received words\nRed team starts\nCap - /hint phrase [num. words]\n/cdnend - '
            'to stop game')
        set_codenames_current_team(message.chat.id, 'red')
        return


@codenames_router.message(Command('hint'))
async def command_codenames_hint_handler(message: Message, command: CommandObject):
    """
       Obsluha přikazu pro ziskání nápovědy ve hře Codenames.

       Args:
           message (Message): Objekt zprávy z Telegramu.
           command (CommandObject): Objekt příkazu z Telegramu.
       """
    args = command.args
    data = args.split()
    try:
        tries = int(data[-1])
        if tries < 1:
            await message.answer('Incorrect number. Should be 1 or more')
            return
    except:
        await message.answer('Error')
        return
    current_team = get_codenames_current_team(message.chat.id)
    if current_team is None:
        await message.answer('No active codenames game in this chat.')
        return
    if current_team == 'red':
        if message.from_user.id != get_codenames_red_cap_id(message.chat.id):
            await message.answer('We need /hint from red capitan')
            return
        set_codenames_tries_red(message.chat.id, int(tries))
    if current_team == 'blue':
        if message.from_user.id != get_codenames_blue_cap_id(message.chat.id):
            await message.answer('We need /hint from blue capitan')
            return
        set_codenames_tries_blue(message.chat.id, int(tries))

    await message.answer(f'Now answering team {current_team}\nType /cdn [word] to answer')


@codenames_router.message(Command('cdn'))
async def command_codenames_cdn_handler(message: Message, command: CommandObject):
    """
    Obsluha přikazu pro hádání slova ve hře Codenames.

    Args:
        message (Message): Objekt zprávy z Telegramu.
        command (CommandObject): Objekt příkazu z Telegramu.
    """
    word = command.args
    if word == '':
        await message.answer('Type word')
        return

    current_team = get_codenames_current_team(message.chat.id)
    if current_team is None:
        await message.answer('No active codenames game in this chat.')
        return

    if current_team != 'blue' and current_team != 'red':
        await message.answer('Cap should make hint')
        return

    chat_id = message.chat.id
    black_word = get_codenames_black_word(chat_id)
    all_words = get_codenames_all_words(chat_id)
    red_words = get_codenames_red_words(chat_id)
    blue_words = get_codenames_blue_words(chat_id)

    if current_team == 'red':
        ids_red = get_codenames_red_team_ids(chat_id)
        if message.from_user.id not in ids_red:
            await message.answer('You are not in red team')
            return
        tries = get_codenames_tries_red(chat_id)
        if tries <= 0:
            await message.answer('You have no more tries.\nNext team!')
            return
        if black_word == word:
            await message.answer('Game over. Team red lost')
            return
        if tries > 0:
            if word in all_words:
                set_codenames_opened_word(chat_id, word)
                await message.answer(f'Word found!\n{create_codenames_table_for_players(chat_id)}')
                if word in blue_words:
                    await message.answer('It was blue word. Next team: Blue')
                    set_codenames_tries_red(chat_id, 0)
                    set_codenames_current_team(chat_id, 'blue')

                if list_contains_elements_of_list(get_codenames_opened_words(chat_id),
                                                  get_codenames_blue_words(chat_id)):
                    await message.answer('Blue team won! All words opened\nGame dropped')
                    drop_codenames_game(message.chat.id)
                    return
                if list_contains_elements_of_list(get_codenames_opened_words(chat_id),
                                                  get_codenames_red_words(chat_id)):
                    await message.answer('Red team won! All words opened\nGame dropped')
                    drop_codenames_game(message.chat.id)
                    return
            else:
                await message.answer('No words found')
            set_codenames_tries_red(chat_id, tries - 1)
            if tries - 1 == 0:
                set_codenames_tries_red(chat_id, 0)
                set_codenames_current_team(chat_id, 'blue')
                await message.answer('Stop. Now time of blue team')

        ######################

    if current_team == 'blue':
        ids_blue = get_codenames_blue_team_ids(chat_id)
        if message.from_user.id not in ids_blue:
            await message.answer('You are not in blue team')
            return
        tries = get_codenames_tries_blue(chat_id)
        if tries <= 0:
            await message.answer('You have no more tries.\nNext team!')
            return
        if black_word == word:
            await message.answer('Game over. Team blue lost')
            drop_codenames_game(chat_id)
            return
        if tries > 0:
            if word in all_words:
                set_codenames_opened_word(chat_id, word)
                await message.answer(f'Word found!\n{create_codenames_table_for_players(chat_id)}')
                if word in red_words:
                    await message.answer('It was red word. Next team: Red')
                    set_codenames_tries_blue(chat_id, 0)
                    set_codenames_current_team(chat_id, 'red')
                    return

                if list_contains_elements_of_list(get_codenames_opened_words(chat_id),
                                                  get_codenames_blue_words(chat_id)):
                    await message.answer('Blue team won! All words opened\nGame dropped')
                    drop_codenames_game(message.chat.id)
                    return

                if list_contains_elements_of_list(get_codenames_opened_words(chat_id),
                                                  get_codenames_red_words(chat_id)):
                    await message.answer('Red team won! All words opened\nGame dropped')
                    drop_codenames_game(message.chat.id)
                    return
            else:
                await message.answer('No words found')
            set_codenames_tries_blue(chat_id, tries - 1)
            if tries - 1 == 0:
                set_codenames_tries_blue(chat_id, 0)
                set_codenames_current_team(chat_id, 'red')
                await message.answer('Stop. Now time of red team')


@codenames_router.message(Command('cdnend'))
async def command_codenames_end_handler(message: Message):
    """
      Obsluha přikazu pro ukončení hry Codenames.

      Args:
          message (Message): Objekt zprávy z Telegramu.
      """
    drop_result = drop_codenames_game(message.chat.id)
    if drop_result is None:
        await message.answer('Nothing games to drop')
        return
    await message.answer('Codenames game successfully dropped')
