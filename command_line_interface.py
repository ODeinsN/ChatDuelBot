import asyncio
import os
import threading
import time
from sys import platform

import pytchat

import CBDGUI.GUI.utils.WebDataUpdater as wdu
import chat_analyser
from CBDGUI.GUI.models import WebData
from StreamChat import StreamChat


class CMDInterface:

    def __init__(self):
        self.CA = chat_analyser.ChatAnalyser()
        self.streams: dict[str, StreamChat] = {}
        self.CA.load_question_txt()

    def connect_to_chat(self, link: str, name: str, translate: bool = False):
        try:
            self.streams.update({name: StreamChat(link, name, translate)})
            if self.streams[name].stream.is_alive():
                print(f"> Connected to {name} Stream")
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

    def input_yes_or_no(self, text: str):
        """
        loops user input until correct answer
        returns true if user typed 'y' or 'yes'
        returns false if iser typed 'n' or 'no'
        """
        while 42:
            input_str = input(text).lower()
            if input_str in {'y', 'yes', 'n', 'no'}:
                return bool(input_str in {'y', 'yes'})

    @staticmethod
    def get_int_input(text: str = ""):
        while 42:
            try:
                value = int(input(text))
                return value
            except ValueError:
                print("> This is not a number. Try Again")

    def print_top_words(self, amount_top_words: int, amount_example_comments: int, no_output: bool = False):
        """
        Prints top words and writes them into WebData.top_comments

        i know its bad, deal with it
        """
        top_words = self.CA.get_top_words(amount_top_words)
        if len(top_words) == 0:
            if not no_output:
                print("> No comments submitted")
                return
        top_comments = []
        for word in top_words:
            data = self.CA.convert_counter_entry_to_dict(word, amount_example_comments)
            text = data['text'] if not self.CA.straw_poll_mode else data['pool_text']
            data['text'] = text
            if not no_output:
                print(f'"{text}": {data["amount"]}, {data["percentage"]}%')
            for comment_text in data['comment_list']:
                if not no_output:
                    print(f'\t{comment_text}')
            top_comments.append(data)
        return top_comments

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
            option: str = input(f'> enter word {i + 1}: ')
            option.lower()
            self.CA.add_straw_poll_option(i + 1, option)

    def start_chat_duel(self):
        WebData.comment_rate_history.clear()
        WebData.comment_counter_history.clear()
        WebData.top_comments.clear()
        WebData.current_question = ''

        print(f'command prefix: {self.CA.command_prefix}')
        if len(self.streams) == 0:
            print("> No Livestreams found.")
            return

        for i in range(len(self.CA.questions)):
            print(f'{[i]}: {self.CA.questions[i]}')
        question_id = -1
        while 42:
            question_id = self.get_int_input('> Select question: ')
            if 0 <= question_id < len(self.CA.questions):
                break
            print('> IndexOutOfRange')

        self.CA.single_submission_mode = not self.input_yes_or_no('> Allow multiple submissions from one user?[y/n]: ')

        straw_poll_mode: bool = self.input_yes_or_no("> is this a straw poll? [y/n]: ")

        if straw_poll_mode:
            self.init_straw_poll()

        duration: int = self.get_int_input("> Pls enter duration in seconds: ")
        start_time = time.time()

        self.CA.reset()
        self.CA._is_cd_running = True
        self.CA.current_question = self.CA.questions[question_id]

        stream_reader_threads: list[threading.Thread] = []
        for key in self.streams:
            stream = self.streams[key]
            stream_reader_threads.append(self.analyse_chat(stream.stream, stream.translation_on))

        temp = self.CA.comment_counter
        wait_time = 1  # seconds

        self.print_comment_receive_stats(duration, start_time, temp, wait_time)

        print('> time finished')
        self.CA._is_cd_running = False
        for thread in stream_reader_threads:
            thread.join()

    def print_comment_receive_stats(self, duration, start_time, temp, wait_time):
        while time.time() < start_time + duration:
            try:
                time.sleep(wait_time)
                print(
                    f"{self.CA.comment_counter} comments received. {round(start_time + duration - time.time())} seconds left.")
                comment_counter_delta = self.CA.comment_counter - temp
                temp = self.CA.comment_counter
                comment_rate = round(comment_counter_delta / wait_time, 2)

                WebData.comment_counter_history.append(self.CA.comment_counter)
                WebData.comment_rate_history.append(comment_rate)
                WebData.top_comments = self.print_top_words(5, 3, True)
                WebData.current_question = self.CA.current_question

                wdu.write_data_into_file(comment_rate=WebData.comment_rate_history,
                                         comment_counter=WebData.comment_counter_history,
                                         top_words=WebData.top_comments,
                                         current_question=self.CA.current_question)

                print(f'received {comment_rate} comments per second.\n')

            except KeyboardInterrupt:
                print('KeyboardInterrupt')
                break

    async def execute(self, command: int):
        self.clear()
        if command == 0:
            exit()

        elif command == 1:
            link = input("> Pls enter chat link or ID [youtube.com/video/watch?v=<ID>]: ")
            name = input("> Pls enter a name: ")
            translate: bool = self.input_yes_or_no("> Translate answers?[y/n]: ")
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
