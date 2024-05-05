from unittest import TestCase

from sqlalchemy.orm import Session

from database import engine, Base, register_guess_new_game, GuessTheWord,\
    get_guess_full_word, get_guessed_part_word, set_guessed_part_word, User, drop_game, \
    check_available_game, register_user_new_game, \
    get_game_users, give_user_score, \
    leave_user_from_all_chats, register_new_codenames_game, CodeNames, \
    join_blue_codenames, join_red_codenames, leave_codenames, info_codenames, join_blue_capitan, join_red_capitan, \
    start_codenames_game, drop_codenames_game, get_codenames_all_words, get_codenames_red_words, \
    get_codenames_blue_words, get_codenames_black_word, get_codenames_opened_words, set_codenames_opened_word, \
    get_codenames_red_cap_id, set_codenames_current_team, get_codenames_current_team, set_codenames_tries_blue, \
    get_codenames_tries_blue, get_codenames_blue_team_ids, get_codenames_red_team_ids, register_alias_game, \
    get_alias_words
from handlers.alias_handler import generate_alias_time_text
from handlers.codenames_handler import list_contains_elements_of_list
from handlers.guess_the_word_handlers import create_users_data_text, generate_connection_text


class TestAlias(TestCase):
    def test_seconds_greater_than_5(self):
        seconds = 10
        expected_result = 'You have 5 - 10 seconds left'
        self.assertEqual(generate_alias_time_text(seconds), expected_result)

    def test_seconds_equal_to_5(self):
        seconds = 5
        expected_result = 'You have 5 seconds left'
        self.assertEqual(generate_alias_time_text(seconds), expected_result)

    def test_seconds_less_than_5(self):
        seconds = 3
        expected_result = 'You have 3 seconds left'
        self.assertEqual(generate_alias_time_text(seconds), expected_result)


class TestCodenames(TestCase):
    def test_contains_elements(self):
        list1 = [1, 2, 3, 4, 5]
        list2 = [2, 4]
        self.assertTrue(list_contains_elements_of_list(list1, list2))

    def test_does_not_contain_elements(self):
        list1 = [1, 2, 3, 4, 5]
        list2 = [2, 6]
        self.assertFalse(list_contains_elements_of_list(list1, list2))


class TestUser:
    def __init__(self, username, score):
        self.username = username
        self.score = score


class TestGuessTheWord(TestCase):

    def test_create_users_data_text(self):
        users_data = [
            TestUser('user1', 100),
            TestUser('user2', 200),
            TestUser('user3', 300)
        ]

        expected_result = 'user1 : 100\nuser2 : 200\nuser3 : 300\n'

        self.assertEqual(create_users_data_text(users_data), expected_result)

    def test_empty_users_data(self):
        users_data = []
        expected_result = ''
        self.assertEqual(create_users_data_text(users_data), expected_result)

    def test_seconds_greater_than_5(self):
        seconds = 10
        expected_result = 'You have some time to connect the game.\nType /connect to connect\n5 - 10 seconds left'
        self.assertEqual(generate_connection_text(seconds), expected_result)

    def test_seconds_equal_to_5(self):
        seconds = 5
        expected_result = 'You have some time to connect the game.\nType /connect to connect\n5 seconds left'
        self.assertEqual(generate_connection_text(seconds), expected_result)

    def test_seconds_less_than_5(self):
        seconds = 3
        expected_result = 'You have some time to connect the game.\nType /connect to connect\n3 seconds left'
        self.assertEqual(generate_connection_text(seconds), expected_result)

    def test_seconds_equal_to_0(self):
        seconds = 0
        expected_result = 'You have some time to connect the game.\nType /connect to connect\n0 seconds left'
        self.assertEqual(generate_connection_text(seconds), expected_result)


class TestDatabaseFunctions(TestCase):

    def setUp(self):
        Base.metadata.create_all(bind=engine)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)

    def test_register_guess_new_game(self):
        chat_id = 123
        question = "Test question"
        full_word = "Test full word"
        guessed_word = "Test guessed word"
        register_guess_new_game(question, full_word, guessed_word, chat_id)
        with Session(bind=engine) as session:
            game = session.query(GuessTheWord).filter_by(chat_id=chat_id).first()
            self.assertIsNotNone(game)
            self.assertEqual(game.question, question)
            self.assertEqual(game.full_word, full_word)
            self.assertEqual(game.guessed_word, guessed_word)


    def test_get_guess_full_word(self):
        chat_id = 123
        full_word = "Test full word"
        with Session(bind=engine) as session:
            game = GuessTheWord(chat_id=chat_id, full_word=full_word)
            session.add(game)
            session.commit()

        returned_word = get_guess_full_word(chat_id)
        self.assertEqual(returned_word, full_word)

    def test_get_guessed_part_word(self):
        chat_id = 123
        guessed_word = "Test guessed word"
        with Session(bind=engine) as session:
            game = GuessTheWord(chat_id=chat_id, guessed_word=guessed_word)
            session.add(game)
            session.commit()
        returned_word = get_guessed_part_word(chat_id)
        self.assertEqual(returned_word, guessed_word)

    def test_set_guessed_part_word(self):
        chat_id = 123
        guessed_word = "Test guessed word"
        new_guessed_word = "New guessed word"
        with Session(bind=engine) as session:
            game = GuessTheWord(chat_id=chat_id, guessed_word=guessed_word)
            session.add(game)
            session.commit()

        set_guessed_part_word(new_guessed_word, chat_id)

        with Session(bind=engine) as session:
            game = session.query(GuessTheWord).filter_by(chat_id=chat_id).first()
            self.assertEqual(game.guessed_word, new_guessed_word)

    def test_drop_game(self):
        chat_id = 123
        with Session(bind=engine) as session:
            game = GuessTheWord(chat_id=chat_id)
            session.add(game)
            user1 = User(username="user1", telegram_id=111, guess_the_word_chat_id=chat_id)
            user2 = User(username="user2", telegram_id=222, guess_the_word_chat_id=chat_id)
            session.add_all([user1, user2])
            session.commit()

        users_data = drop_game(chat_id)

        with Session(bind=engine) as session:
            game_exists = session.query(GuessTheWord).filter_by(chat_id=chat_id).first()
            self.assertIsNone(game_exists)

        self.assertIsInstance(users_data, list)
        self.assertEqual(len(users_data), 2)
        self.assertTrue(all(isinstance(user, User) for user in users_data))

    def test_check_available_game(self):
        chat_id = 123
        with Session(bind=engine) as session:
            game = GuessTheWord(chat_id=chat_id)
            session.add(game)
            session.commit()

        available_game = check_available_game(chat_id)
        self.assertIsNotNone(available_game)

    def test_register_user_new_game(self):
        chat_id = 123
        telegram_id = 111
        with Session(bind=engine) as session:
            game = GuessTheWord(chat_id=chat_id)
            session.add(game)
            session.commit()

        result = register_user_new_game("user1", telegram_id, chat_id)

        self.assertTrue(result)

        result = register_user_new_game("user2", telegram_id, chat_id)
        self.assertFalse(result)


    def test_get_game_users(self):
        chat_id = 123
        with Session(bind=engine) as session:
            game = GuessTheWord(chat_id=chat_id)
            user1 = User(username="user1", telegram_id=111, guess_the_word_chat_id=chat_id)
            user2 = User(username="user2", telegram_id=222, guess_the_word_chat_id=chat_id)
            session.add_all([game, user1, user2])
            session.commit()

        users = get_game_users(chat_id)

        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 2)
        self.assertEqual(users, [111, 222])

    def test_give_user_score(self):
        telegram_id = 111
        with Session(bind=engine) as session:
            user = User(username="user1", telegram_id=telegram_id, score=0)
            session.add(user)
            session.commit()

        give_user_score(telegram_id)

        with Session(bind=engine) as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            self.assertEqual(user.score, 1)

    def test_leave_user_from_all_chats(self):
        telegram_id = 111
        with Session(bind=engine) as session:
            user1 = User(username="user1", telegram_id=telegram_id, guess_the_word_chat_id=123)
            user2 = User(username="user2", telegram_id=telegram_id, guess_the_word_chat_id=456)
            session.add_all([user1, user2])
            session.commit()

        leave_user_from_all_chats(telegram_id)

        with Session(bind=engine) as session:
            users = session.query(User).filter_by(telegram_id=telegram_id).all()
            self.assertEqual(len(users), 0)


    def test_register_new_codenames_game(self):
        chat_id = 123
        words_all = "apple,banana,orange"
        words_red = "apple,banana"
        words_blue = "orange"
        word_black = "watermelon"
        register_new_codenames_game(words_all, words_red, words_blue, word_black, chat_id)

        with Session(bind=engine) as session:
            game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
            self.assertIsNotNone(game)
            self.assertEqual(game.words_all, words_all)
            self.assertEqual(game.words_red, words_red)
            self.assertEqual(game.words_blue, words_blue)
            self.assertEqual(game.word_black, word_black)

    def test_join_blue_codenames(self):
        user_id = 111
        chat_id = 123
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)

        result = join_blue_codenames(user_id, chat_id)

        self.assertEqual(result, 'You joined blue team')

        with Session(bind=engine) as session:
            game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
            blue_team_ids = game.ids_blue.split()
            self.assertIn(str(user_id), blue_team_ids)

    def test_join_red_codenames(self):
        user_id = 111
        chat_id = 123
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)

        result = join_red_codenames(user_id, chat_id)

        self.assertEqual(result, 'You joined red team')

        with Session(bind=engine) as session:
            game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
            red_team_ids = game.ids_red.split()
            self.assertIn(str(user_id), red_team_ids)

    def test_leave_codenames(self):
        user_id = 111
        chat_id = 123
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)
        join_blue_codenames(user_id, chat_id)

        result = leave_codenames(chat_id, user_id)

        self.assertEqual(result, 'You have left blue team')

        with Session(bind=engine) as session:
            game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
            blue_team_ids = game.ids_blue.split()
            self.assertNotIn(str(user_id), blue_team_ids)

    def test_info_codenames(self):
        chat_id = 123
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)

        result = info_codenames(chat_id)
        expected_result = f'Red cap: 0\n\nBlue cap:0\n'
        self.assertEqual(result, expected_result)

    def test_join_blue_capitan(self):
        chat_id = 123
        user_id = 111
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)

        join_blue_capitan(chat_id, user_id)

        with Session(bind=engine) as session:
            codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
            self.assertEqual(codenames_game.id_capitan_blue, user_id)

    def test_join_red_capitan(self):
        chat_id = 123
        user_id = 111
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)

        join_red_capitan(chat_id, user_id)

        with Session(bind=engine) as session:
            codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
            self.assertEqual(codenames_game.id_capitan_red, user_id)

    def test_start_codenames_game(self):
        chat_id = 123
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)

        join_blue_capitan(chat_id, 111)
        join_red_capitan(chat_id, 222)

        result = start_codenames_game(chat_id)
        self.assertTrue(result)

    def test_drop_codenames_game(self):
        chat_id = 123
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)

        result = drop_codenames_game(chat_id)

        self.assertTrue(result)

        with Session(bind=engine) as session:
            codenames_game = session.query(CodeNames).filter_by(chat_id=chat_id).first()
            self.assertIsNone(codenames_game)

    def test_get_codenames_all_words(self):
        chat_id = 123
        register_new_codenames_game("apple banana orange", "apple", "banana", "watermelon", chat_id)

        result = get_codenames_all_words(chat_id)
        print(result)

        self.assertListEqual(result, ["apple", "banana", "orange"])

    def test_get_codenames_red_words(self):
        chat_id = 123
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)

        result = get_codenames_red_words(chat_id)

        self.assertListEqual(result, ["apple"])

    def test_get_codenames_blue_words(self):
        chat_id = 123
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)

        result = get_codenames_blue_words(chat_id)

        self.assertListEqual(result, ["banana"])

    def test_get_codenames_black_word(self):
        chat_id = 123
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)

        result = get_codenames_black_word(chat_id)

        self.assertEqual(result, "watermelon")

    def test_get_codenames_opened_words(self):
        chat_id = 123
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)

        result = get_codenames_opened_words(chat_id)

        self.assertListEqual(result, [])

    def test_set_codenames_opened_word(self):
        chat_id = 123
        word = "apple"
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)

        set_codenames_opened_word(chat_id, word)

        result = get_codenames_opened_words(chat_id)
        self.assertIn(word, result)

    def test_get_codenames_red_cap_id(self):
        chat_id = 123
        cap_id = 111
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)
        join_red_capitan(chat_id, cap_id)

        result = get_codenames_red_cap_id(chat_id)

        self.assertEqual(result, cap_id)

    def test_set_codenames_current_team(self):
        chat_id = 123
        team_color = "blue"
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)

        set_codenames_current_team(chat_id, team_color)

        result = get_codenames_current_team(chat_id)

        self.assertEqual(result, team_color)

    def test_set_codenames_tries_blue(self):
        chat_id = 123
        tries = 3
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)

        set_codenames_tries_blue(chat_id, tries)

        result = get_codenames_tries_blue(chat_id)

        self.assertEqual(result, tries)

    def test_get_codenames_blue_team_ids(self):
        chat_id = 123
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)
        join_blue_codenames(111, chat_id)

        result = get_codenames_blue_team_ids(chat_id)

        self.assertIn(111, result)

    def test_get_codenames_red_team_ids(self):
        chat_id = 123
        register_new_codenames_game("apple,banana,orange", "apple", "banana", "watermelon", chat_id)
        join_red_codenames(222, chat_id)

        result = get_codenames_red_team_ids(chat_id)

        self.assertIn(222, result)

    def test_get_alias_words(self):
        chat_id = 123
        words = ["apple", "banana", "orange"]
        register_alias_game(chat_id, words)

        result = get_alias_words(chat_id)

        self.assertListEqual(result, words)
