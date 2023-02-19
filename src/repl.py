
import os
import sys

from lib.readline import ReadLine
from core.engine import Engine

engine = Engine()

class REPL:

    def __init__(self) -> None:
        ...

    def loop(self) -> None:
        for count, _ in enumerate(iter(bool, True)):
            try:
                stdout = self.cycle(input(f"[{count}] > "))
            except KeyboardInterrupt:
                self.handle_exit()
            except EOFError:
                ...
            except SystemExit:
                self.on_exit()

    def pre_loop(self, stdin: str) -> str:
        return stdin

    def main_loop(self, stdin: str) -> str:
        return stdin

    def post_loop(self, stdin: str) -> str:
        return stdin

    def cycle(self, stdin: str) -> str:
        for process in [self.pre_loop, self.main_loop, self.post_loop]:
            stdin = process(stdin)
        return stdin

    def on_start(self) -> None:
        print('\033[H\033[J', end='') # move to sepirate lib
        ReadLine()

    def on_exit(self) -> None:
        sys.exit(0)

    def handle_exit(self) -> None:
        response = input("Exit: ", style="red")
        if response in ["y", "Y", "yes", "Yes", "YES"]:
            self.on_exit()

    def run(self) -> None:
        self.on_start()
        self.loop()
