from command_line_interface import CMDInterface
import asyncio
import txt_reader


def main():
    cmd = CMDInterface()
    asyncio.run(cmd.run())
    # print(txt_reader.get_word_set('files/bad_words_german.txt'))


if __name__ == "__main__":
    main()