from copy import copy

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import Session, DeclarativeBase, relationship
from sqlalchemy import Column, String, Date, BigInteger, Integer

from constants import diplomacy_max_players

sqlite_database = "sqlite:///database.db"

engine = create_engine(sqlite_database, echo=True)


class Base(DeclarativeBase):
    pass


class Alias(Base):
    __tablename__ = "alias"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer)
    words = Column(String)


class CodeNames(Base):
    __tablename__ = "codenames"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer)
    words_all = Column(String)
    words_opened = Column(String)
    words_red = Column(String)
    words_blue = Column(String)
    word_black = Column(String)
    ids_red = Column(String)
    ids_blue = Column(String)
    id_capitan_red = Column(BigInteger)
    id_capitan_blue = Column(BigInteger)
    tries_blue = Column(Integer)
    tries_red = Column(Integer)
    current_team = Column(String)


class GuessTheWord(Base):
    __tablename__ = "guesstheword"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer)
    question = Column(String)
    full_word = Column(String)
    guessed_word = Column(String)
    users = relationship("User", back_populates="guesstheword")


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger)
    username = Column(String)
    score = Column(Integer)
    guess_the_word_chat_id = Column(Integer, ForeignKey("guesstheword.chat_id"))
    guesstheword = relationship("GuessTheWord", back_populates="users")


Base.metadata.create_all(bind=engine)


def register_guess_new_game(question, full_word, guessed_word, chat_id):
    with Session(autoflush=False, bind=engine) as session:
        session.query(GuessTheWord).filter_by(chat_id=chat_id).delete()
        session.commit()
        game = GuessTheWord(chat_id=chat_id, question=question, full_word=full_word, guessed_word=guessed_word)
        session.add(game)
        session.commit()


def get_guess_full_word(chat_id):
    with Session(autoflush=False, bind=engine) as session:
        try:
            game = session.query(GuessTheWord).filter_by(chat_id=chat_id).first()
            return game.full_word
        except:
            return False


def get_guessed_part_word(chat_id):
    with Session(autoflush=False, bind=engine) as session:
        try:
            game = session.query(GuessTheWord).filter_by(chat_id=chat_id).first()
            return game.guessed_word
        except:
            return False


def set_guessed_part_word(guessed_word, chat_id):
    with Session(autoflush=False, bind=engine) as session:
        try:
            game = session.query(GuessTheWord).filter_by(chat_id=chat_id).first()
            game.guessed_word = guessed_word
            session.commit()
        except:
            return False


def drop_game(chat_id):
    with Session(autoflush=False, bind=engine) as session:
        try:
            game = session.query(GuessTheWord).filter_by(chat_id=chat_id).first()
            users_data = session.query(User).filter_by(guess_the_word_chat_id=game.chat_id).all()
            session.query(GuessTheWord).filter_by(chat_id=chat_id).delete()
            session.query(User).filter_by(guess_the_word_chat_id=game.chat_id).delete()
            session.commit()
        except:
            return None
    return users_data


def check_available_game(chat_id):
    with Session(autoflush=False, bind=engine) as session:
        return session.query(GuessTheWord).filter_by(chat_id=chat_id).first()


def register_user_new_game(username, telegram_id, chat_id):
    with Session(autoflush=False, bind=engine) as session:
        game = session.query(GuessTheWord).filter_by(chat_id=chat_id).first()
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user in game.users:
            return False
        if user is None:
            user = User(username=username, telegram_id=telegram_id, score=0)
            game.users.append(user)
            session.add(game)
            session.commit()
            return True
        return False


def get_game_users(chat_id):
    with Session(autoflush=False, bind=engine) as session:
        game = session.query(GuessTheWord).filter_by(chat_id=chat_id).first()
        users = game.users
        ids = [user.telegram_id for user in users]
        if len(ids) > 0:
            return ids
    return False


def give_user_score(telegram_id):
    with Session(autoflush=False, bind=engine) as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        user.score += 1
        session.commit()


def leave_user_from_all_chats(telegram_id):
    with Session(autoflush=False, bind=engine) as session:
        session.query(User).filter_by(telegram_id=telegram_id).delete()
        session.commit()


def register_new_codenames_game(words_all, words_red, words_blue, word_black, chat_id):
    with Session(autoflush=False, bind=engine) as session:
        session.query(CodeNames).filter_by(chat_id=chat_id).delete()
        session.commit()
        game = CodeNames(chat_id=chat_id, words_all=words_all, words_opened='', words_red=
        words_red, words_blue=words_blue, ids_red='', ids_blue='', id_capitan_red=0,
                         id_capitan_blue=0, word_black=word_black)
        session.add(game)
        session.commit()


def join_blue_codenames(user_id, chat_id):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        if codenames_game is None:
            return 'No games found'
        user_id = str(user_id)
        blue_team_ids = codenames_game.ids_blue.split()
        red_team_ids = codenames_game.ids_red.split()
        if user_id in blue_team_ids:
            return 'You already in blue team'
        if user_id in red_team_ids:
            red_team_ids.remove(user_id)
            codenames_game.ids_red = ' '.join(red_team_ids)
            blue_team_ids.append(user_id)
            codenames_game.ids_blue = ' '.join(blue_team_ids)
            session.add(codenames_game)
            session.commit()
            return 'Successfully team changed to blue'

        blue_team_ids.append(user_id)
        codenames_game.ids_blue = ' '.join(blue_team_ids)
        session.add(codenames_game)
        session.commit()
        return 'You joined blue team'


def join_red_codenames(user_id, chat_id):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        if codenames_game is None:
            return 'No games found'
        user_id = str(user_id)
        blue_team_ids: list = codenames_game.ids_blue.split()
        red_team_ids: list = codenames_game.ids_red.split()
        if user_id in red_team_ids:
            return 'You already in red team'
        if user_id in blue_team_ids:
            blue_team_ids.remove(user_id)
            codenames_game.ids_blue = ' '.join(blue_team_ids)
            red_team_ids.append(user_id)
            codenames_game.ids_red = ' '.join(red_team_ids)
            session.add(codenames_game)
            session.commit()
            return 'Successfully team changed to red'

        red_team_ids.append(user_id)
        codenames_game.ids_red = ' '.join(red_team_ids)
        session.add(codenames_game)
        session.commit()
        return 'You joined red team'


def info_codenames(chat_id):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        if codenames_game is None:
            return 'No games found'
        red_ids = codenames_game.ids_red
        blue_ids = codenames_game.ids_blue
        red_cap = codenames_game.id_capitan_red
        blue_cap = codenames_game.id_capitan_blue
    return (f'Red cap: {red_cap}'
            f'\n{red_ids}'
            f'\nBlue cap:{blue_cap}'
            f'\n{blue_ids}')


def leave_codenames(chat_id, user_id):
    user_id = str(user_id)
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        if codenames_game is None:
            return 'No games found'
        red_team_ids: list = codenames_game.ids_red.split()
        blue_team_ids: list = codenames_game.ids_blue.split()
        if user_id in red_team_ids:
            red_team_ids.remove(user_id)
            codenames_game.ids_red = ' '.join(red_team_ids)
            session.add(codenames_game)
            session.commit()
            return 'You have left red team'
        if user_id in blue_team_ids:
            blue_team_ids.remove(user_id)
            codenames_game.ids_blue = ' '.join(blue_team_ids)
            session.add(codenames_game)
            session.commit()
            return 'You have left blue team'
        if user_id == str(codenames_game.id_capitan_red):
            codenames_game.id_capitan_red = 0
            session.add(codenames_game)
            session.commit()
            return 'You have left position of red cap'

        if user_id == str(codenames_game.id_capitan_blue):
            codenames_game.id_capitan_blue = 0
            session.add(codenames_game)
            session.commit()
            return 'You have left position of red blue'

    return 'No teams found'


def join_blue_capitan(chat_id, user_id):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        codenames_game.id_capitan_blue = user_id
        session.add(codenames_game)
        session.commit()


def join_red_capitan(chat_id, user_id):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        codenames_game.id_capitan_red = user_id
        session.add(codenames_game)
        session.commit()


def start_codenames_game(chat_id):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        if codenames_game.id_capitan_blue != 0 and codenames_game.id_capitan_red != 0:
            users_red: list = codenames_game.ids_red.split()
            users_blue: list = codenames_game.ids_blue.split()
            if len(users_blue) > -1 and len(users_red) > -1:  # change after testing
                return True
    return False


def drop_codenames_game(chat_id):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        if codenames_game is None:
            return None
        session.query(CodeNames).filter_by(chat_id=chat_id).delete()
        session.commit()
        return True


def get_codenames_all_words(chat_id) -> list:
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        return codenames_game.words_all.split()


def get_codenames_red_words(chat_id) -> list:
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        return codenames_game.words_red.split()


def get_codenames_blue_words(chat_id) -> list:
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        return codenames_game.words_blue.split()


def get_codenames_black_word(chat_id):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        return codenames_game.word_black


def get_codenames_opened_words(chat_id) -> list:
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        return codenames_game.words_opened.split()


def set_codenames_opened_word(chat_id, word):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        codenames_game.words_opened += f' {word}'
        session.add(codenames_game)
        session.commit()


def get_codenames_red_cap_id(chat_id):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        return codenames_game.id_capitan_red


def get_codenames_blue_cap_id(chat_id):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        return codenames_game.id_capitan_blue


def get_codenames_tries_blue(chat_id):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        return codenames_game.tries_blue


def get_codenames_tries_red(chat_id):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        return codenames_game.tries_red


def get_codenames_current_team(chat_id):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        if codenames_game is None:
            return None
        return codenames_game.current_team


def set_codenames_current_team(chat_id, team_color):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        codenames_game.current_team = team_color
        session.add(codenames_game)
        session.commit()


def set_codenames_tries_blue(chat_id, tries):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        codenames_game.tries_blue = tries
        session.add(codenames_game)
        session.commit()


def set_codenames_tries_red(chat_id, tries):
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        codenames_game.tries_red = tries
        session.add(codenames_game)
        session.commit()


def get_codenames_blue_team_ids(chat_id) -> list:
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        ids_blue = list(map(int, codenames_game.ids_blue.split()))
        return ids_blue


def get_codenames_red_team_ids(chat_id) -> list:
    with Session(autoflush=False, bind=engine) as session:
        codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
        ids_red = list(map(int, codenames_game.ids_red.split()))
        return ids_red


def get_alias_words(chat_id) -> list:
    with Session(autoflush=False, bind=engine) as session:
        alias_game = session.query(Alias).filter_by(chat_id=chat_id).first()
        words = alias_game.words.split()
        return words


def remove_alias_word(chat_id, word):
    with Session(autoflush=False, bind=engine) as session:
        alias_game = session.query(Alias).filter_by(chat_id=chat_id).first()
        words = alias_game.words.split()
        words.remove(word)
        alias_game.words = ' '.join(words)
        session.add(alias_game)
        session.commit()


def register_alias_game(chat_id, words: list):
    with Session(autoflush=False, bind=engine) as session:
        session.query(Alias).filter_by(chat_id=chat_id).delete()
        session.commit()
        words = ' '.join(words)
        alias_game = Alias(chat_id=chat_id, words=words)
        session.add(alias_game)
        session.commit()
