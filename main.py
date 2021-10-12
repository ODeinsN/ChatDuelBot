from command_line_interface import CMDInterface
import asyncio
import CBDGUI.GUI.utils.WebDataUpdater as wdu


def main():
    # cmd = CMDInterface()
    # asyncio.run(cmd.run())
    comment_rate = [0, 7, 2, 3, 1, 19, 4]
    comment_counter = [0]
    for x in comment_rate:
        comment_counter.append(comment_counter[-1] + x)
    top_words = [{'text': 'test1', 'amount': 10, 'percentage': 15.2, 'comment_list': ["example comment 1", "example comment 2"]},
                 {'text': 'test2', 'amount': 17, 'percentage': 23, 'comment_list': ["example comment 1", "example comment 2"]}]

    wdu.write_data_into_file(comment_rate=comment_rate, comment_counter=comment_counter, top_words=top_words)


if __name__ == "__main__":
    main()
