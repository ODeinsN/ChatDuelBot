import asyncio
import random

import command_line_interface
from unit_tests import ChatMessage


async def main():
    cmd = command_line_interface.CMDInterface()
    answers = {1: "Putin", 2: 'Trump'}
    cmd.CA.set_straw_poll_options(answers)
    cmd.CA.set_straw_poll_mode(True)
    for _ in range(20):
        await cmd.CA.add_comment_to_wordlist(ChatMessage(f'!cd {random.randint(0,1)+1}'), translate=False)
    cmd.print_top_words(2, 0)

if __name__ == "__main__":
    asyncio.run(main())