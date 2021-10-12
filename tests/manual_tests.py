import asyncio
import random

import command_line_interface
from unit_tests import ChatMessage


def main():
    # asyncio.run(straw_poll_test())
    asyncio.run(normal_chat_test(1000))


async def straw_poll_test():
    cmd = command_line_interface.CMDInterface()
    answers = {1: "Putin", 2: 'Trump'}
    cmd.CA.set_straw_poll_options(answers)
    cmd.CA.set_straw_poll_mode(True)
    for _ in range(20):
        await cmd.CA.add_comment(ChatMessage(f'!cd {random.randint(0, 1) + 1}'), translate=False)
    cmd.print_top_words(2, 0)


async def normal_chat_test(n: int):
    cmd = command_line_interface.CMDInterface()
    answers = ['Ich mag bier', 'bier', 'tee', 'Koffein', 'Schlafmangel', 'partys']
    for _ in range(n):
        await cmd.CA.add_comment(ChatMessage(f'!cd {answers[random.randint(0, len(answers) - 1)]}'))
    cmd.print_top_words(3, 2)
    cmd.print_result("tee")
    cmd.print_result("ich mag bier")


if __name__ == "__main__":
    main()
