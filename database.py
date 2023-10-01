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
    guess_the_word_id = Column(Integer, ForeignKey("guesstheword.id"))
    guesstheword = relationship("GuessTheWord", back_populates="users")


Base.metadata.create_all(bind=engine)


def register_guess_new_game(question, full_word, guessed_word):
    with Session(autoflush=False, bind=engine) as session:
        session.query(GuessTheWord).delete()
        session.commit()
        game = GuessTheWord(question=question, full_word=full_word, guessed_word=guessed_word)
        session.add(game)
        session.commit()


def get_guess_full_word():
    with Session(autoflush=False, bind=engine) as session:
        try:
            games = session.query(GuessTheWord).all()
            game = games[-1]
            return game.full_word
        except:
            return False


def get_guessed_part_word():
    with Session(autoflush=False, bind=engine) as session:
        try:
            games = session.query(GuessTheWord).all()
            game = games[-1]
            return game.guessed_word
        except:
            return False

def set_guessed_part_word(guessed_word):
    with Session(autoflush=False, bind=engine) as session:
        try:
            games = session.query(GuessTheWord).all()
            game = games[-1]
            game.guessed_word = guessed_word
            session.commit()
        except:
            return False


def register_user_new_game(username, telegram_id):
    with Session(autoflush=False, bind=engine) as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user is None:
            user = User(username=username, telegram_id=telegram_id, score=0)
            session.add(user)
            session.commit()
            return True
    return False


def drop_game():
    with Session(autoflush=False, bind=engine) as session:
        users_data = session.query(User).all()
        session.query(GuessTheWord).delete()
        session.query(User).delete()
        session.commit()
    return users_data


def check_available_game():
    with Session(autoflush=False, bind=engine) as session:
        return len(session.query(GuessTheWord).all())


def get_game_users():
    with Session(autoflush=False, bind=engine) as session:
        users = session.query(User).all()
        ids = [user.telegram_id for user in users]
        if len(ids) > 0:
            return ids
    return False


def give_user_score(telegram_id):
    with Session(autoflush=False, bind=engine) as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        user.score += 1
        session.commit()
