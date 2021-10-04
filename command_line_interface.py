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

    def clear(self):
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
            percentage = round(amount/self.CA.comment_counter) * 100
            print(f'"{text}": {amount}, {percentage}%')
            for _ in range(amount_example_comments if amount >= amount_example_comments else amount):
                print(f'\t{self.CA.word_distribution_list[text].get_random_comment()}')

    @staticmethod
    def print_user_menu():
        print("""
------------------------------
> [0]: Exit Programm
> [1]: Add Livestrean
> [2]: Start ChatDuell
> [3]: Show Results
        """)

    def analyse_chat(self, stream: pytchat.LiveChat, translate: bool = False, specific_answers_mode: bool = False, specific_words: dict[int, str] = None):
        thread = threading.Thread(target=asyncio.run, args=(self.CA.read_chat(stream, translate, specific_answers_mode, specific_words),))
        thread.start()

    def start_chat_duel(self):
        if len(self.streams) == 0:
            print("> No Livestreams found.")
            return

        straw_poll_mode: bool = True if input("> Set specific answers [y/n]?: ") in ("y", "yes", "j", "ja") else False

        straw_poll_options: dict[int, str] = {}
        if straw_poll_mode:
            n: int = self.get_int_input("How many?: ")
            for i in range(n):
                straw_poll_options.update({i: input(f'enter word {i}: ').lower()})

        duration: int = self.get_int_input("> Pls enter duration in seconds: ")
        start_time = time.time()

        self.CA.reset()
        self.CA.is_CD_running = True

        for key in self.streams:
            stream = self.streams[key]
            self.analyse_chat(stream.stream, stream.translation_on, straw_poll_mode, straw_poll_options)
        # print("> reading chat. Waiting for end of timer. Press [CTRL] + [SHIFT] + x to stop earlier.")
        while time.time() < start_time + duration:
            time.sleep(1)
            print(f"{self.CA.comment_counter} comments received. {round(start_time + duration - time.time())} seconds left.")
        self.CA.is_CD_running = False

    async def execute(self, command: int):
        # clear()
        if command == 0:
            exit()

        elif command == 1:
            link = input("> Pls enter chat link or ID [youtube.com/video/<ID>]: ")
            name = input("> Pls enter a name: ")
            translate: bool = input("> Translate answeres?[y/n]: ").lower() in ['y', 'yes']
            self.connect_to_chat(link, name, translate)

        elif command == 2:
            self.start_chat_duel()

        elif command == 3:
            if self.CA.comment_counter == 0:
                print("> No Comments have been submitted")
                return
            n_top_words = self.get_int_input("> Pls enter amount of top words: ")
            n_example_comments = self.get_int_input("> Pls enter amount of example comments: ")
            self.print_top_words(n_top_words, n_example_comments)

        # elif command == 4:
        #     self.print_streams()
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