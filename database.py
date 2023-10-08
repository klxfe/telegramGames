from copy import copy

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import Session, DeclarativeBase, relationship
from sqlalchemy import Column, String, Date, BigInteger, Integer

sqlite_database = "sqlite:///database.db"

engine = create_engine(sqlite_database, echo=True)


class Base(DeclarativeBase):
    pass


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

        game = session.query(GuessTheWord).filter_by(chat_id=chat_id).first()
        users_data = session.query(User).filter_by(guess_the_word_chat_id=game.chat_id).all()
        session.query(GuessTheWord).filter_by(chat_id = chat_id).delete()
        session.query(User).filter_by(guess_the_word_chat_id=game.chat_id).delete()

        session.commit()
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
        game = session.query(GuessTheWord).filter_by(chat_id = chat_id).first()
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

