import asyncio
import json
import random
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from texts.buttons import text_play_guess_the_word
from database import register_guess_new_game, register_user_new_game, drop_game, check_available_game, get_game_users, \
    get_guess_full_word, give_user_score, get_guessed_part_word, set_guessed_part_word, leave_user_from_all_chats
from constants import seconds_helper, seconds_to_start

guess_the_word_router = Router(name=__name__)

my_queue = asyncio.Queue()


def generate_connection_text(seconds):
    """
    Generuje zprávu pro připojení ke hře, ukazuje kolik zbývá času na připojení.

    Args:
        Kolik zbývá sekund na připojení.

    Returns:
        str: Zpráva pro připojení ke hře.
    """
    if seconds - 5 > 0:
        return f'You have some time to connect the game.\nType /connect to connect\n{seconds - 5} - {seconds} seconds left'
    return f'You have some time to connect the game.\nType /connect to connect\n{seconds} seconds left'


def create_users_data_text(users_data):
    """
    Generuje textovou prezetací aktualního počtu bodů uživatelů.

    Args:
        users_data (list): Seznam údajů uživatele.

    Returns:
        str: Textová zpráva obsahující údaje uživatele.
    """
    text = ''
    for user in users_data:
        text += f'{user.username} : {user.score}\n'
    return text


async def reveal_loop(message: Message, full_word):
    """
    Asynchronní cyklus pro generaci nápovědy hadaného slova ve hře.

    Args:
        message (Message): Objekt zprávy z Telegramu.
        full_word (str): Celé slovo, které je potřeba odhádnout.
    """

    while full_word == get_guess_full_word(message.chat.id):
        await asyncio.sleep(seconds_helper)
        try:
            guessed_part = get_guessed_part_word(message.chat.id).split(' ')
        except:
            return
        indexes = []
        for i in range(len(guessed_part)):
            if guessed_part[i] == '__':
                indexes.append(i)
        try:
            index = random.choice(indexes)
        except IndexError:
            return
        guessed_part[index] = full_word[index]
        guessed_part = ' '.join(guessed_part)
        if full_word != get_guess_full_word(message.chat.id):  # check changes in database
            return
        set_guessed_part_word(guessed_part, message.chat.id)
        await message.answer(f'Helper: {guessed_part}')

        if guessed_part.replace(' ', '') == full_word:
            return


async def connection_time(message: Message, question, hidden_word, word):
    """
        Asynchronní funkce pro vypočet času připojení ke hře a začátku hry.

        Args:
            message (Message): Objekt zprávy z Telegramu.
            question (str): Otázka.
            hidden_word (str): Skrýté slovo k odhádnutí.
            word (str): Celé slovo, které je potřeba odhádnout.
        """
    seconds = seconds_to_start
    await my_queue.put(1)
    while seconds > 0:
        if seconds <= 10:
            await asyncio.sleep(1)
            seconds -= 1
            await message.edit_text(generate_connection_text(seconds))
            continue
        await message.edit_text(generate_connection_text(seconds))
        await asyncio.sleep(10)
        seconds -= 10
    await message.edit_text('Time is over. Game has started.')
    await message.answer(f'Q:{question}\n{hidden_word}')
    await reveal_loop(message, word)
    await my_queue.get()


def generate_new_word(chat_id):
    """
     Generuje nové slovo pro hru.

     Args:
         chat_id (int): Id chatu

     Returns:
         dict: Slovník dat o novém slově a otazce k němu ve hře.
     """
    with open('sources/guess_the_word.json', encoding="utf-8") as f:
        words = json.load(f)
    word_data = random.choice(words)
    word_data['hidden_word'] = (len(word_data['word']) * '__ ')[:-1]
    hidden_word = word_data['hidden_word']
    word = word_data['word']
    question = word_data['question']
    register_guess_new_game(question, word, hidden_word, chat_id)
    return word_data


@guess_the_word_router.message(F.text == text_play_guess_the_word)
async def message_guess_the_word_handler(message: Message):
    """
        Obsluha zprávy pro začátek hry Guess the Word.

        Args:
            message (Message): Objekt zprávy z Telegramu.
        """
    if check_available_game(message.chat.id):
        await message.answer('Some games are in cache.\nType /end to end all games and try one more time')
        return
    word_data = generate_new_word(message.chat.id)
    msg = await message.answer(generate_connection_text(seconds_to_start))
    await connection_time(msg, word_data['question'], word_data['hidden_word'], word_data['word'])


@guess_the_word_router.message(Command('leave'))
async def message_leave_handler(message: Message):
    """
    Obsluha přikazu /leave pro opuštění všech her.

    Args:
        message (Message): Objekt zprávy z Telegramu.
    """
    leave_user_from_all_chats(message.from_user.id)
    await message.answer('You left all chats')


@guess_the_word_router.message(Command('connect'))
async def message_connect_handler(message: Message):
    """
     Obsluha přikazu /connect pro připojení uživatele ke hře.

     Args:
         message (Message): Objekt zprávy z Telegramu.
     """
    if my_queue.empty():
        await message.answer(f'No available games')
        return
    if register_user_new_game(message.from_user.full_name, message.from_user.id, message.chat.id):
        await message.answer(f'{message.from_user.full_name} connected.')
    else:
        await message.answer(
            f'{message.from_user.full_name}, you has already connected. \n/leave - leave all games from all chats')


@guess_the_word_router.message(Command('end'))
async def message_end_handler(message: Message):
    """
    Obsluha přikazu /end pro ukončení všech her v daném chatu.

    Args:
        message (Message): Objekt zprávy z Telegramu.
    """
    users_data = drop_game(message.chat.id)
    print(users_data)
    if users_data is None:
        await message.answer('You have ended all games.')
        return
    text = create_users_data_text(users_data)
    await message.answer('You have ended all games\n' + text)


@guess_the_word_router.message(Command('answer'))
async def message_answer_handler(message: Message, command: CommandObject):
    """
       Obsluha přikazu /answer pro kontrolu odpovědi od uživatele.

       Args:
           message (Message): Objekt zprávy z Telegramu.
           command (CommandObject): Objekt příkazu z Telegramu.
       """
    if not check_available_game(message.chat.id):
        await message.answer("No available game now")
        return
    user_ids = get_game_users(message.chat.id)
    if not user_ids:
        await message.reply("No users in game")
        return
    if message.from_user.id not in user_ids:
        print('-------------', user_ids)
        await message.reply("You don't participate in game")
        return
    data = command.args
    if data.lower() != get_guess_full_word(message.chat.id):
        await message.reply("Yor answer is incorrect")
        return
    give_user_score(message.from_user.id)
    await message.reply(f'Great! Correct answer!, {message.from_user.full_name}')
    word_data = generate_new_word(message.chat.id)
    await message.answer(f'Q:{word_data["question"]}\n{word_data["hidden_word"]}')
    await reveal_loop(message, word_data["word"])
