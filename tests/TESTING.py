import asynctest
import chat_analyser
from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class ChatMessage():
    message: str


async def fill_word_list(word: str, n: int, translate: bool = False):
    for _ in range(n):
        c = ChatMessage(f"!cd {word}")
        await chat_analyser.add_comment_to_wordlist(c, translate)


class UnitTestCases(asynctest.TestCase):
    def tearDown(self):
        GLOBALS.reset()

    @staticmethod
    async def test_top_comment_list_without_translation():
        await fill_word_list("bier", 10)
        await fill_word_list("tee", 15)
        await fill_word_list("beer", 6)
        top = chat_analyser.get_top_words(3)
        print(top)
        assert top[0][0] == "tee"

    @staticmethod
    async def test_top_comment_translation():
        await fill_word_list("bier", 10)
        await fill_word_list("tee", 15)
        await fill_word_list("Beer", 6, True)
        top = chat_analyser.get_top_words(3)
        print(top)
        assert top[0][0] == "bier"


if __name__ == "__main__":
    asynctest.main()