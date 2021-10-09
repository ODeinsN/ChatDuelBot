import threading
import time
import pytchat
import chat_analyser
import os
import asyncio
from sys import platform
from StreamChat import StreamChat
from matplotlib import pyplot as plt


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
            if amount >= amount_example_comments:
                for _ in range(amount_example_comments):
                    print(f'\t{self.CA.word_distribution_dict[text].get_random_comment()}')
            else:
                for i in range(amount):
                    print(f'\t{self.CA.word_distribution_dict[text].get_comment(i)}')

    def print_result(self, words: str):
        words = words.lower()
        words = words.split()
        results = self.CA.get_results(words)
        print(f'> "{results["word"]}": {results["amount"]} votes = {results["percentage"]}%')

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

    def init_straw_poll(self):
        self.CA.set_straw_poll_mode(True)
        n: int = self.get_int_input("> How many options?: ")
        for i in range(n):
            option: str = input(f'> enter word {i+1}: ')
            option.lower()
            self.CA.add_straw_poll_option(i+1, option)

    def start_chat_duel(self):
        if len(self.streams) == 0:
            print("> No Livestreams found.")
            return

        straw_poll_mode: bool = bool(input("> Set specific answers [y/n]?: ") in ("y", "yes", "j", "ja"))

        if straw_poll_mode:
            self.init_straw_poll()

        duration: int = self.get_int_input("> Pls enter duration in seconds: ")
        start_time = time.time()

        self.CA.reset()
        self.CA._is_CD_running = True

        stream_reader_threads: list[threading.Thread] = []
        for key in self.streams:
            stream = self.streams[key]
            stream_reader_threads.append(self.analyse_chat(stream.stream, stream.translation_on))

        # print("> reading chat. Waiting for end of timer. Press [CTRL] + [SHIFT] + x to stop earlier.")

        temp = self.CA.comment_counter
        wait_time = 1  # seconds

        self.print_comment_receive_stats(duration, start_time, temp, wait_time)

        print('> time finished')
        self.CA._is_CD_running = False
        for thread in stream_reader_threads:
            thread.join()

    def print_comment_receive_stats(self, duration, start_time, temp, wait_time):
        comment_rate_history = []
        while time.time() < start_time + duration:
            time.sleep(wait_time)
            print(f"{self.CA.comment_counter} comments received. {round(start_time + duration - time.time())} seconds left.")
            comment_counter_delta = self.CA.comment_counter - temp
            temp = self.CA.comment_counter
            comment_rate = round(comment_counter_delta / wait_time, 2)
            self.CA.append_comment_rate_history(comment_rate)
            comment_rate_history.append(comment_rate)
            print(f'received {comment_rate} comments per second.\n')
        plt.plot(comment_rate_history)
        plt.ylabel('comment rate')
        plt.show()

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
        for key in self.CA.word_distribution_dict:
            print(f'{key}: {self.CA.word_distribution_dict[key].comment_counter}')

    def print_streams(self):
        if len(self.streams) == 0:
            print("> No Streams available.")
            return
        for key in self.streams:
            print(self.streams[key])
