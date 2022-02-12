from .lexer import Lexer
from .grammars import STATEMENT
from typing import List


def Parser(inp: str) -> List:
    tokens = Lexer(inp).tokens
    out = STATEMENT(tokens, debug=True)

    if not out[0]:
        raise ValueError(
            f"Parse Error in input statement beginning from Token '{tokens[out[1]].token}'"
        )
    return out
