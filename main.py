from command_line_interface import CMDInterface
import asyncio


def main():
    cmd = CMDInterface()
    asyncio.run(cmd.run())


if __name__ == "__main__":
    main()