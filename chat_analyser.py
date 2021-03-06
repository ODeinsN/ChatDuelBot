import asyncio
import datetime
import threading
from collections import Counter
from dataclasses import dataclass
from threading import Thread
from typing import Any

import pytchat
from cache import async_lru
from googletrans import Translator

import txt_reader
from CommentContainer import CommentContainer


@dataclass
class ChatAnalyser:
    _word_distribution_dict: dict[str, CommentContainer]
    _comment_counter: int
    _is_cd_running: bool
    _cd_start_time: datetime.datetime
    _command_prefix: str
    _banned_words: set[str]
    _local_top_words: list[dict[str, Any]]
    _questions: list[str]
    _current_question: str
    _user_set: set[str]
    _single_submission_mode: bool

    def __init__(self):
        self._word_distribution_dict = {}
        self._comment_counter = 0
        self._is_cd_running = False
        self._straw_poll_mode: bool = False
        self._straw_poll_options: dict[int, str] = {}
        self._command_prefix = '!'
        self._banned_words = set()
        self._banned_words.update(txt_reader.get_word_set('files/bad_words_german.txt'))
        self._questions = []
        self._current_question = ""
        self._user_set = set()
        self._single_submission_mode = False

    def load_question_txt(self):
        with open('files/questions.txt', 'r') as file:
            for line in file:
                self._questions.append(line.replace('\n', ''))

    @property
    def questions(self):
        return self._questions

    @property
    def current_question(self):
        return self._current_question

    def is_word_banned(self, word: str) -> bool:
        """
        returns True if word is a banned word
        """
        return word in self._banned_words

    def set_straw_poll_mode(self, mode: bool):
        self._straw_poll_mode = mode

    def set_straw_poll_options(self, options: list[int, str]):
        self._straw_poll_options = options

    def reset(self):
        self._word_distribution_dict.clear()
        self._comment_counter = 0
        self._is_cd_running = False
        self._current_question = ''
        self.user_set.clear()

    def get_top_words(self, n: int):
        """
        Calculates and returns top_words
        """
        c = Counter(self._word_distribution_dict)
        most_common = c.most_common(n)
        return most_common

    @async_lru.AsyncLRU(maxsize=1024)
    async def translate_text(self, text: str, dest: str, src: str) -> str:
        t = Translator()
        translated = t.translate(text, dest=dest, src=src).text
        return translated

    async def add_comment(self, chat_message, translate: bool = False):
        message: str = chat_message.message.lower()
        translator = Translator()
        if self.single_submission_mode:
            if chat_message.author.name in self.user_set:
                return
        if not message.startswith(self._command_prefix) or message == self._command_prefix or len(message) > 64:
            return
        message = message.removeprefix(self._command_prefix)
        words: list[str] = message.lower().split()

        # remove duplicate words
        words = list(set(words))

        for word in words:
            if self.is_word_banned(word):
                return

        if self._straw_poll_mode:
            if len(words) > 1:
                return
            found: bool = False
            for key, value in self._straw_poll_options.items():
                if str(key) in words or value in words:
                    found = True
                    break
            if not found:
                return

        if translate and not self._straw_poll_mode:
            for i in range(len(words)):
                words[i] = await self.translate_text(words[i], dest='de', src='en')

        for word in words:
            word_as_key: int = -1
            try:
                word_as_key = int(word)
            except ValueError:
                pass
            if word_as_key in self.straw_poll_options.keys():
                self.add_comment_to_wordlist(chat_message, self.straw_poll_options[word_as_key])
            else:
                self.add_comment_to_wordlist(chat_message, word)

        if self.single_submission_mode:
            self.user_set.add(chat_message.author.name)

        self._comment_counter += 1

    @property
    def user_set(self):
        lock = threading.Lock()
        with lock:
            return self._user_set

    @property
    def single_submission_mode(self):
        lock = threading.Lock()
        with lock:
            return self._single_submission_mode

    # adding plus 15 seconds to compensate time differences between local and youtube time
    def is_message_out_of_time(self, message_time: str, start_time: datetime.datetime) -> bool:
        x = datetime.datetime.strptime(message_time, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(seconds=15)
        return x < start_time

    async def read_chat(self, chat, translate: bool = False):
        self._cd_start_time = datetime.datetime.now()
        print(self._cd_start_time)
        try:
            while chat.is_alive() and self._is_cd_running:
                async for comment in chat.get().async_items():
                    if self.is_message_out_of_time(comment.datetime, start_time=self._cd_start_time):
                        continue
                    t = Thread(target=asyncio.run, args=(self.add_comment(comment, translate),))
                    t.start()
                    t.join()
            chat.raise_for_status()
        except pytchat.ChatDataFinished:
            print("> Chat data finished.")
        except Exception as e:
            print(type(e), str(e))

    def add_comment_to_wordlist(self, chat_message, word):
        lock = threading.Lock()
        with lock:
            if word in self._word_distribution_dict:
                self._word_distribution_dict[word].add_comment(chat_message)
            else:
                self._word_distribution_dict.update({word: CommentContainer(chat_message)})

    def get_results(self, words) -> dict[str, None]:
        result_dict: dict[str, None] = {}
        if self._comment_counter == 0:
            print('> no comments have been submitted')
            return {}
        if not self.are_words_in_word_list(words):
            print(f'> "{str(words)}" was never submitted')
            return {}
        for word in words:
            amount = self._word_distribution_dict[word].get_comment_counter()
            percentage = round(amount * 100 / self._comment_counter, 2)
            result_dict.update({'word': word, 'percentage': percentage, 'amount': amount})
        return result_dict

    # Checks if at least 1 word from parameter "words" exists in word_distribution_dict
    def are_words_in_word_list(self, words: list[str]):
        for word in words:
            if word in self._word_distribution_dict:
                return True
        return False

    def get_word_percentage(self, word):
        amount = self._word_distribution_dict[word].get_comment_counter()
        return round(amount * 100 / self._comment_counter, 2)

    def get_comment_counter(self):
        return self._comment_counter

    def add_straw_poll_option(self, index, option):
        self._straw_poll_options.update({index: option})

    @property
    def comment_counter(self):
        return self._comment_counter

    @property
    def word_distribution_dict(self):
        return self._word_distribution_dict

    @property
    def straw_poll_options(self):
        return self._straw_poll_options

    @property
    def straw_poll_mode(self):
        return self._straw_poll_mode

    @property
    def is_cd_running(self) -> bool:
        return self._is_cd_running

    @is_cd_running.setter
    def is_cd_running(self, a: bool):
        self._is_cd_running = a

    @property
    def banned_words(self):
        return self._banned_words

    @banned_words.setter
    def banned_words(self, val):
        self._banned_words = val

    def convert_counter_entry_to_dict(self, entry: tuple[str, CommentContainer], amount_example_comments: int) -> dict[
        str, Any]:
        text = entry[0]
        comment_list: list[str] = []
        amount: int = entry[1].get_comment_counter()
        percentage = round(amount * 100 / self.comment_counter, 2)
        text_as_int: int = 0
        is_int: bool = False
        try:
            text_as_int: int = int(text)
            is_int = True
        except ValueError:
            pass
        pool_text = ''
        if self.straw_poll_mode:
            if is_int:
                pool_text = self.straw_poll_options[text_as_int]
            else:
                pool_text = text
                
        if amount >= amount_example_comments:
            for _ in range(amount_example_comments):
                comment_list.append(self._word_distribution_dict[text].get_random_comment())
        else:
            for i in range(amount):
                comment_list.append(self.word_distribution_dict[text].get_comment(i))
        data: dict[str, Any] = {
            'text': text,
            'amount': amount,
            'percentage': percentage,
            'pool_text': pool_text,
            'comment_list': comment_list
        }
        return data

    @property
    def command_prefix(self):
        return self._command_prefix

    @current_question.setter
    def current_question(self, value):
        self._current_question = value

    @single_submission_mode.setter
    def single_submission_mode(self, value):
        self._single_submission_mode = value
