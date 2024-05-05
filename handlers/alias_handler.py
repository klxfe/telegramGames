import asyncio
import json
import random

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from callbacks.alias import StartCallback, YesNoCallback
from keyboards.play_alias import get_inline_keyboard_game_alias
from keyboards.start_alias_keyboard import get_inline_keyboard_start_alias
from texts.buttons import text_play_alias
from database import  register_alias_game, get_alias_words, remove_alias_word

alias_router = Router(name=__name__)

WIN_SCORE = 50


class GameState(StatesGroup):
    first_team_name = State()
    second_team_name = State()
    first_team_score = State()
    second_team_score = State()
    words_counter = State()


@alias_router.message(F.text == text_play_alias)
async def message_alias_handler(message: Message, state: FSMContext):
    """
        Obsluha zpráv pro příkazy bota.

        Args:
        message (Message): Objekt zprávy z Telegramu.
        state (FSMContext): Konečný stav.
    """
    if message.chat.type != 'private':
        await message.answer('You can do this only in private chat')
        return
    await message.answer('Type first team name')
    await state.set_state(GameState.first_team_name)


@alias_router.message(GameState.first_team_name)
async def get_first_team_name(message: Message, state: FSMContext):
    """
    Obsluha zpráv pro získání názvu prvního týmu.

    Args:
        message (Message): Objekt zprávy z Telegramu.
        state (FSMContext): Konečný stav.
    """
    await state.update_data(first_team_name=message.text)
    await message.answer(f'Team {message.text} registered!\nType second team name')
    await state.set_state(GameState.second_team_name)


@alias_router.message(GameState.second_team_name)
async def get_second_team_name(message: Message, state: FSMContext):
    """
     Obsluha zpráv pro získání názvu druhého týmu.

     Args:
         message (Message): Objekt zprávy z Telegramu.
         state (FSMContext): Konečný stav.
     """
    await state.update_data(second_team_name=message.text)
    await state.set_state(GameState.first_team_score)
    data = await state.get_data()

    await state.update_data(first_team_score='0')
    await state.update_data(second_team_score='0')
    await state.update_data(words_counter='0')
    register_alias_game(message.chat.id, generate_all_words())
    await message.answer(f'Team {message.text} registered!\nPress start to play',
                         reply_markup=get_inline_keyboard_start_alias())


def generate_alias_time_text(seconds):
    """
    Generuje text pro zobrarení času ve hře Alias.

    Args:
        seconds (int): Kolik sekund zbývá

    Returns:
        str: Text pro zobrazení času.
    """
    if seconds - 5 > 0:
        return f'You have {seconds - 5} - {seconds} seconds left'
    return f'You have {seconds} seconds left'


async def get_state_info(state):
    """
    Ziskává data ohledně aktuálního stavu FSM.

    Args:
        state (FSMContext): Konečný stav.

    Returns:
        list: Informace o aktuálním stavu hry.
    """
    state_info = await state.get_state()
    state_info = state_info.split(':')[1]
    return state_info


async def start_timer(state: FSMContext, message: Message, seconds, msg: Message):
    """
    Spouští timer i aktualizuje stav hry Alias s ohledém na zbývající čas.

    Args:
        state (FSMContext): Konečný stav.
        message (Message): Objekt zprávy z Telegramu.
        seconds (int): Počet sekund pro timer.
        msg (Message): Objekt zprávy z Telegramu pro úpravu.
    """
    state_info = await get_state_info(state)
    while seconds > 0:
        if state_info != 'first_team_score' and state_info != 'second_team_score':
            return

        if seconds <= 10:
            await asyncio.sleep(1)
            seconds -= 1
            await message.edit_text(generate_alias_time_text(seconds))
            continue
        await message.edit_text(generate_alias_time_text(seconds))
        await asyncio.sleep(10)
        seconds -= 10
    counter_data = await state.get_data()
    await state.update_data(words_counter=int(counter_data['words_counter']) + 1)
    data = await state.get_data()

    first_team_score = data['first_team_score']
    second_team_score = data['second_team_score']
    first_team_name = data['first_team_name']
    second_team_name = data['second_team_name']
    words_counter = data['words_counter']
    state_info = await get_state_info(state)
    if state_info == 'first_team_score':
        await state.set_state(GameState.second_team_score)
        now_team = second_team_name
    elif state_info == 'second_team_score':
        await state.set_state(GameState.first_team_score)
        now_team = first_team_name

    if int(second_team_score) > WIN_SCORE and int(second_team_score) > int(first_team_score) and int(
            words_counter) % 2 == 0:
        await msg.edit_text(
            f'Time left\n{first_team_name}:{first_team_score}\n{second_team_name}:{second_team_score}'
            f'\nTeam  {second_team_name} won')
        await state.clear()

    elif int(first_team_score) > WIN_SCORE and int(first_team_score) > int(second_team_score) and int(
            words_counter) % 2 == 0:
        await msg.edit_text(
            f'Time left\n{first_team_name}:{first_team_score}\n{second_team_name}:{second_team_score}'
            f'\nTeam  {first_team_name} won')
        await state.clear()

    elif int(first_team_score) > WIN_SCORE and int(first_team_score) == int(second_team_score) and int(
            words_counter) % 2 == 0:
        await msg.edit_text(
            f'Time left\n{first_team_name}:{first_team_score}\n{second_team_name}:{second_team_score}'
            f'\nBoth teams won')
        await state.clear()
    else:
        await msg.edit_text(
            f'Time left\n{first_team_name}:{first_team_score}\n{second_team_name}:{second_team_score}'
            f'\nNow team: {now_team}'
            f'\nWords: {words_counter}')
        await msg.edit_reply_markup(reply_markup=get_inline_keyboard_start_alias())

    await message.delete()


def generate_all_words():
    """
    Generuje seznam slov pro hru Alias.

    Returns:
        list: Seznam slov.
    """
    with open('sources/alias.json', encoding="utf-8") as f:
        words = json.load(f)
    return words


def generate_random_word(chat_id):
    """
    generuje náhodné slovo s seznamu slov pro hru Alias.

    Args:
        chat_id: Id chatu

    Returns:
        str: Náhodně vybrané slovo se seznamu.
    """
    words = get_alias_words(chat_id)
    if len(words) == 0:
        return 'No more words'
    word = random.choice(words)
    remove_alias_word(chat_id, word)
    return word


@alias_router.callback_query(StartCallback.filter(F.foo == 'start'))
async def start_callback_foo(query: CallbackQuery, state: FSMContext):
    """
     Obsluha CallbackQuery pro začátek hry.

     Args:
         query (CallbackQuery): Objekt CallbackQuery z Telegramu.
         state (FSMContext): Konečný stav.
     """
    await query.message.edit_text(generate_alias_time_text(11))

    chat_id = query.message.chat.id

    msg = await query.message.answer(f'You started the game. \nWord: {generate_random_word(chat_id)}',
                                     reply_markup=get_inline_keyboard_game_alias())
    await start_timer(state, query.message, 10, msg)


@alias_router.callback_query(StartCallback.filter(F.foo == 'end'))
async def start_callback_foo(query: CallbackQuery, state: FSMContext):
    """
    Obsluha CallbackQuery pro ukončení hry.

    Args:
        query (CallbackQuery): Objekt CallbackQuery z Telegramu.
        state (FSMContext): Konečný stav.
    """
    data = await state.get_data()
    first_team_score = data['first_team_score']
    second_team_score = data['second_team_score']
    first_team_name = data['first_team_name']
    second_team_name = data['second_team_name']
    await query.message.edit_text(
        f'End of the game!\n{first_team_name}:{first_team_score}\n{second_team_name}:{second_team_score}')
    await state.clear()


async def send_message_word(query, operation):
    """
    Posílá zprávu se slovem pro hru Alias.

    Args:
        query: Objekt Query z Telegramu.
        operation: Operace, která se zobrazí v zprávě (+1 nebo -1).
    """
    random_word = generate_random_word(query.message.chat.id)
    await query.message.edit_text(f'{operation}1 Word: {random_word}',
                                  reply_markup=get_inline_keyboard_game_alias())


@alias_router.callback_query(YesNoCallback.filter(F.foo == 'answer'))
async def answer_callback_foo(query: CallbackQuery, callback_data: YesNoCallback, state: FSMContext):
    """
    Obsluha CallbackQuery pro odpověd Ano/Ne.

    Args:
        query (CallbackQuery): Objekt CallbackQuery z Telegramu.
        callback_data (YesNoCallback): Data CallbackQuery.
        state (FSMContext): Konečný stav.
    """
    answer = callback_data.answer
    state_info = await get_state_info(state)

    data = await state.get_data()

    if answer.lower() == 'yes':

        await send_message_word(query, '+')
        if state_info == 'first_team_score':
            await state.update_data(first_team_score=int(data['first_team_score']) + 1)
        if state_info == 'second_team_score':
            await state.update_data(second_team_score=int(data['second_team_score']) + 1)

    elif answer.lower() == 'no':
        await send_message_word(query, '-')

        if state_info == 'first_team_score':
            await state.update_data(first_team_score=int(data['first_team_score']) - 1)
        if state_info == 'second_team_score':
            await state.update_data(second_team_score=int(data['second_team_score']) - 1)
