from exceldb.parser.parser import Parser
from exceldb.parser.grammars import STATEMENT
from exceldb.parser.lexer import Lexer

print(Parser("SELECT * FROM database;"))
