from .reader import Reader
from . import tokens
from . import enums
from typing import Any, Optional, Type
from enum import Enum


class Lexer:
    def __init__(self, inp: str) -> None:
        self.inp = inp
        self.reader = Reader(inp)
        self.tokens = []
        self.index = -1

        self.tokenize()

    def tokenize(self) -> None:
        def contains(enum: Type[Enum], value: Any) -> bool:
            return any(item.value == value for item in enum)

        def isalpha(string: str) -> bool:
            return string[0].isalpha() and all(
                char.isalpha()
                or char
                in ["_", "@", "$", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
                for char in string[1:]
            )

        while not self.reader.isEOF():
            i = self.reader.consume()

            if contains(enums.IGN, i):
                continue

            if contains(enums.CTX, i):
                self.tokens.append(tokens.CTX(i))
                continue

            if contains(enums.END, i):
                self.tokens.append(tokens.EOL(i))
                continue

            if i in ["'", '"']:
                string = ""
                previous = ""

                while not self.reader.isEOF():
                    next = self.reader.consume()

                    if next == i:
                        if previous != "\\" and self.reader.peek() != i:
                            break
                        string = string[:-1]
                    string += next

                    if next == "\\" and previous == "\\":
                        previous += "\\"
                    else:
                        previous = next

                self.tokens.append(tokens.VAL(string))
                continue

            if i.isdigit():
                index = 1
                number = i
                add = True

                while not self.reader.isEOF(self.reader.index + index - 1):
                    next = self.reader.peek(index)

                    if next.isdigit() or (next == "." and not "." in number):
                        number += next
                        index += 1
                        continue

                    if (
                        contains(enums.IGN, next)
                        or contains(enums.END, next)
                        or contains(enums.CTX, next)
                        or contains(enums.SOPR, next)
                    ):
                        break

                    add = False
                    break

                if add:
                    self.reader.consume(index - 1)
                    self.tokens.append(
                        tokens.VAL(float(number))
                        if "." in number
                        else tokens.INTVAL(int(number))
                    )
                    continue

            if i in ["=", ">", "<", "!"]:
                word = i

                if i in [">", "<", "!"] and self.reader.peek() == "=":
                    self.reader.consume()
                    word += "="

                self.tokens.append(tokens.SOPR(word))
                continue

            word = i

            while not self.reader.isEOF():
                next = self.reader.peek()

                if (
                    contains(enums.IGN, next)
                    or contains(enums.CTX, next)
                    or contains(enums.SOPR, next)
                    or contains(enums.END, next)
                ):
                    break

                self.reader.consume()
                word += next

            _word = word.upper()
            L = False

            checks = [
                (enums.DDL, tokens.DDL),
                (enums.DML, tokens.DML),
                (enums.TCL, tokens.TCL),
                (enums.DQL, tokens.DQL),
                (enums.HL, tokens.HL),
                (enums.AOPR, tokens.AOPR),
                (enums.BOPR, tokens.BOPR),
                (enums.DT, tokens.DT),
            ]

            for check in checks:
                if contains(check[0], _word):
                    self.tokens.append(check[1](_word, word))
                    L = True

            if L == False:
                if isalpha(word) or word == "*":
                    self.tokens.append(tokens.NAME(word, word))
                else:
                    self.tokens.append(tokens.UKN(word))

        self.tokens.append(tokens.EOF("EOF"))

    def peek(self, k: Optional[int] = None) -> Type[tokens.Token]:
        if k is None:
            k = 1

        return self.tokens[self.index + k]

    def consume(self, k: Optional[int] = None) -> Type[tokens.Token]:
        if k is None:
            k = 1

        self.index += k

        return self.tokens[self.index]
