import threading
import time
import pytchat
import chat_analyser
import os
import asyncio
from sys import platform
from StreamChat import StreamChat


class CMDInterface:

    def __init__(self):
        self.CA = chat_analyser.ChatAnalyser()
        self.streams: dict[str, StreamChat] = {}

    def connect_to_chat(self, link: str, name: str, translate: bool = False):
        try:
            self.streams.update({name: StreamChat(link, name, translate)})
            if self.streams[name].stream.is_alive():
                print(f"> Connected to {name} Stream")
                print(self.streams)
        except pytchat.ChatDataFinished:
            print("> Chat data finished")
        except Exception as e:
            print("> ERROR: Connection to stream FAILED.")
            print(type(e), str(e))

    @staticmethod
    def clear():
        if platform in ["linux", "linux2"]:
            os.system('clear')
        elif platform == "win32":
            os.system('cls')

    @staticmethod
    def get_int_input(text: str = ""):
        while 42:
            try:
                value = int(input(text))
                return value
            except ValueError:
                print("> This is not a number. Try Again")

    def print_top_words(self, amount_top_words: int, amount_example_comments: int):
        top_words = self.CA.get_top_words(amount_top_words)
        if len(top_words) == 0:
            print("> No comments submitted")
            return
        for word in top_words:
            text = word[0]
            amount: int = word[1].get_comment_counter()
            percentage = round(amount * 100 / self.CA.comment_counter, 2)
            print(f'"{self.CA.straw_poll_options[int(text)] if self.CA.straw_poll_mode else text}": {amount}, {percentage}%')
            for _ in range(amount_example_comments if amount >= amount_example_comments else amount):
                print(f'\t{self.CA.word_distribution_list[text].get_random_comment()}')

    def print_result(self, words: str):
        words = words.split()
        if self.CA.comment_counter == 0:
            print('> no comments have been submitted')
            return
        if len(set(words).intersection(set(self.CA.word_distribution_list))) == 0:
            print(f'> "{str(words)}" was never submitted')
            return
        for word in words:
            amount = self.CA.word_distribution_list[word].get_comment_counter()
            percentage = round(amount * 100 / self.CA.comment_counter, 2)
            print(f'> "{word}": {amount} votes = {percentage}%')

    @staticmethod
    def print_user_menu():
        print("""
------------------------------
> [0]: Exit Program
> [1]: Add Livestream
> [2]: Start ChatDuel
> [3]: Show Top Results
> [4]: Show result for word
        """)

    def analyse_chat(self, stream: pytchat.LiveChat, translate: bool = False):
        thread = threading.Thread(target=asyncio.run, args=(self.CA.read_chat(stream, translate),))
        thread.start()
        return thread

    def start_chat_duel(self):
        if len(self.streams) == 0:
            print("> No Livestreams found.")
            return

        straw_poll_mode: bool = bool(input("> Set specific answers [y/n]?: ") in ("y", "yes", "j", "ja"))

        if straw_poll_mode:
            self.CA.set_straw_poll_mode(True)
            n: int = self.get_int_input("> How many options?: ")
            for i in range(n):
                option: str = input(f'> enter word {i+1}: ')
                option.lower()
                self.CA.straw_poll_options.update({i+1: option})

        duration: int = self.get_int_input("> Pls enter duration in seconds: ")
        start_time = time.time()

        self.CA.reset()
        self.CA.is_CD_running = True
        threads: list[threading.Thread] = []

        for key in self.streams:
            stream = self.streams[key]
            threads.append(self.analyse_chat(stream.stream, stream.translation_on))
        # print("> reading chat. Waiting for end of timer. Press [CTRL] + [SHIFT] + x to stop earlier.")

        temp = self.CA.comment_counter
        wait_time = 1  # seconds
        while time.time() < start_time + duration:
            time.sleep(wait_time)
            print(f"{self.CA.comment_counter} comments received. {round(start_time + duration - time.time())} seconds left.")
            comment_counter_delta = self.CA.comment_counter - temp
            temp = self.CA.comment_counter
            print(f'received {round(comment_counter_delta / wait_time, 2)} comments per second.\n')
        print('> time finished')
        self.CA.is_CD_running = False
        for thread in threads:
            thread.join()

    async def execute(self, command: int):
        # clear()
        if command == 0:
            exit()

        elif command == 1:
            link = input("> Pls enter chat link or ID [youtube.com/video/<ID>]: ")
            name = input("> Pls enter a name: ")
            translate: bool = input("> Translate answers?[y/n]: ").lower() in ['y', 'yes']
            self.connect_to_chat(link, name, translate)

        elif command == 2:
            self.start_chat_duel()

        elif command == 3:
            if self.CA.comment_counter == 0:
                print("> No comments have been submitted")
                return
            n_top_words = self.get_int_input("> Pls enter amount of top words: ")
            n_example_comments = self.get_int_input("> Pls enter amount of example comments: ")
            self.print_top_words(n_top_words, n_example_comments)

        elif command == 4:
            words = input("> pls enter word or sentence: ")
            self.print_result(words)
        else:
            print("> ERROR: Unknown Command")

    async def run(self):
        while 42:
            self.print_user_menu()
            command: int = self.get_int_input("> Waiting for user input: ")
            await self.execute(command)

    async def print_word_distribution(self):
        for key in self.CA.word_distribution_list:
            print(f'{key}: {self.CA.word_distribution_list[key].comment_counter}')

    def print_streams(self):
        if len(self.streams) == 0:
            print("> No Streams available.")
            return
        for key in self.streams:
            print(self.streams[key])
