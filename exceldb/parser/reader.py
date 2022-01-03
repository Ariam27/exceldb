from typing import Optional


class Reader:
    def __init__(self, inp: str) -> None:
        self.inp = inp
        self._index = -1

    @property
    def index(self) -> int:
        return self._index

    def peek(self, k: Optional[int] = None) -> str:
        if k is None:
            k = 1

        return self.inp[self._index + k]

    def consume(self, k: Optional[int] = None) -> str:
        if k is None:
            k = 1

        self._index += k

        return self.inp[self._index]

    def isEOF(self, index: Optional[int] = None) -> bool:
        if index is None:
            index = self._index

        return index + 1 == len(self.inp)
