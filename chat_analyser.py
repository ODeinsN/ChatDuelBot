import threading
import time
from collections import Counter
from googletrans import Translator
from cache import async_lru
from typing import Dict
import pytchat
import CommentContainer
from dataclasses import dataclass
from threading import Thread
import asyncio
import datetime
import plotly

"""
If google translator is not working, type in console
$ pip uninstall googletrans
$ pip install googletrans==3.1.0a0
"""


@dataclass
class ChatAnalyser:
    _word_distribution_dict: Dict[str, CommentContainer.CommentContainer]
    _comment_counter: int
    _is_CD_running: bool
    _cd_start_time: datetime.datetime
    _comment_counter_history: list[int]
    _comment_rate_history: list[float]

    def __init__(self):
        self._word_distribution_dict = {}
        self._comment_counter = 0
        self._is_CD_running = False
        self._straw_poll_mode: bool = False
        self._straw_poll_options: dict[int, str] = {}
        self._comment_counter_history = []
        self._comment_rate_history = []

    def set_straw_poll_mode(self, mode: bool):
        self._straw_poll_mode = mode

    def set_straw_poll_options(self, options: list[int, str]):
        self._straw_poll_options = options

    def reset(self):
        self._word_distribution_dict.clear()
        self._comment_counter = 0
        self._is_CD_running = False

    def get_top_words(self, n: int):
        c = Counter(self._word_distribution_dict)
        most_common = c.most_common(n)
        return most_common

    @async_lru.AsyncLRU(maxsize=1024)
    async def translate_text(self, text: str, dest: str, src: str) -> str:
        t = Translator()
        translated = t.translate(text, dest=dest, src=src).text
        return translated

    async def add_comment(self, chat_message, translate: bool = False):
        words = chat_message.message.lower().split()
        translator = Translator()
        if words[0] != "!cd" or len(words) < 2 or len(chat_message.message) > 64:
            return
        words.remove(words[0])

        words = list(set(words))

        if self._straw_poll_mode:
            if len(words) > 1:
                return
            found: bool = False
            for key in self._straw_poll_options.keys():
                if str(key) in words:
                    found = True
                    break
            if not found:
                return

        if translate and not self._straw_poll_mode:
            for i in range(len(words)):
                words[i] = await self.translate_text(words[i], dest='de', src='en')

        for word in words:
            self.add_comment_to_wordlist(chat_message, word)

        self._comment_counter += 1
        self._comment_counter_history.append(self.comment_counter)

    def is_message_out_of_time(self, message_time: str, start_time: datetime.datetime) -> bool:
        x = datetime.datetime.strptime(message_time, '%Y-%m-%d %H:%M:%S')
        return x < start_time

    async def read_chat(self, chat, translate: bool = False):
        self._cd_start_time = datetime.datetime.now()
        while chat.is_alive() and self._is_CD_running:
            # await word_list_UI.print_word_distribution()
            async for comment in chat.get().async_items():
                if chat.is_replay():
                    continue
                if self.is_message_out_of_time(comment.datetime, start_time=self._cd_start_time):
                    continue
                t = Thread(target=asyncio.run, args=(self.add_comment(comment, translate),))
                t.start()
                t.join()
        try:
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
                self._word_distribution_dict.update({word: CommentContainer.CommentContainer(chat_message)})

    """
    Dictionary entry types are:
        'word': str
        'percentage': float
        'amount': int
    """
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

    def plot_message_counter(self):
        return

    def append_comment_rate_history(self, rate):
        if rate < 0:
            return
        self._comment_rate_history.append(rate)
