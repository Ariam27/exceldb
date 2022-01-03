from exceldb.parser.lexer import Lexer
import exceldb.parser.grammars as grammars

statement = """ROLLBACK;"""
tokens = Lexer(statement).tokens[:-1]

rule = vars(grammars)[tokens[0].token]

print(rule == tokens)
print(*rule(tokens), sep="\n")
