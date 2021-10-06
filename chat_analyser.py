import threading
from collections import Counter
from googletrans import Translator
from cache import async_lru
from typing import Dict
import pytchat
import CommentContainer
from dataclasses import dataclass
from threading import Thread
import asyncio

"""
If google translator is not working, type in console
$ pip uninstall googletrans
$ pip install googletrans==3.1.0a0
"""


@dataclass
class ChatAnalyser:
    word_distribution_list: Dict[str, CommentContainer.CommentContainer]
    comment_counter: int
    is_CD_running: bool

    def __init__(self):
        self.word_distribution_list = {}
        self.comment_counter = 0
        self.is_CD_running = False
        self.straw_poll_mode: bool = False
        self.straw_poll_options: dict[int, str] = {}

    def set_straw_poll_mode(self, mode: bool):
        self.straw_poll_mode = mode

    def set_straw_poll_options(self, options: list[int, str]):
        self.straw_poll_options = options

    def reset(self):
        self.word_distribution_list.clear()
        self.comment_counter = 0
        self.is_CD_running = False

    def get_top_words(self, n: int):
        c = Counter(self.word_distribution_list)
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
        if words[0] != "!cd" or len(words) <= 1 or len(chat_message.message) > 64:
            return
        words.remove(words[0])

        words = list(set(words))

        if self.straw_poll_mode:
            if len(words) > 1:
                return
            found: bool = False
            for key in self.straw_poll_options:
                if str(key) in words:
                    found = True
                    break
            if not found:
                return

        if translate and not self.straw_poll_mode:
            for i in range(len(words)):
                words[i] = await self.translate_text(words[i], dest='de', src='en')

        for word in words:
            self.add_comment_to_wordlist(chat_message, word)
        self.comment_counter += 1

    async def read_chat(self, chat, translate: bool = False):
        while chat.is_alive() and self.is_CD_running:
            # await word_list_UI.print_word_distribution()
            for comment in chat.get().sync_items():
                t = Thread(target=asyncio.run, args=(self.add_comment(comment, translate),))
                t.start()
                t.join()
        try:
            chat.raise_for_status()
            print(">Time finished.")
        except pytchat.ChatDataFinished:
            print("> Chat data finished.")
        except Exception as e:
            print(type(e), str(e))

    def add_comment_to_wordlist(self, chat_message, word):
        lock = threading.Lock()
        with lock:
            if word in self.word_distribution_list:
                self.word_distribution_list[word].add_comment(chat_message)
            else:
                self.word_distribution_list.update({word: CommentContainer.CommentContainer(chat_message)})
