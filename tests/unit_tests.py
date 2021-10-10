import asynctest
from chat_analyser import ChatAnalyser
from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class ChatMessage():
    message: str


async def fill_word_list(ca: ChatAnalyser, word: str, n: int, translate: bool = False):
    prefix = '!a '
    for _ in range(n):
        c = ChatMessage(f"{prefix}{word}")
        await ca.add_comment_to_wordlist(c, translate)


class UnitTestCases(asynctest.TestCase):
    def tearDown(self):
        pass

    @staticmethod
    async def test_top_comment_list_without_translation():
        ca = ChatAnalyser()
        await fill_word_list(ca, "bier", 10)
        await fill_word_list(ca, "tee", 15)
        await fill_word_list(ca, "beer", 6)
        top = ca.get_top_words(3)
        print(top)
        assert top[0][0] == "tee"

    @staticmethod
    async def test_top_comment_translation():
        ca = ChatAnalyser()
        await fill_word_list(ca, "bier", 10)
        await fill_word_list(ca, "tee", 15)
        await fill_word_list(ca, "Beer", 6, True)
        top = ca.get_top_words(3)
        print(top)
        assert top[0][0] == "bier"


if __name__ == "__main__":
    asynctest.main()