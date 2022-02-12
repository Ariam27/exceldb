from exceldb.parser.pattern_matching import *

x = Expression["[", ZeroOrOne[OneOrMany[Choice[Instance[int]]]], "]"]
print(x == ["[", 1, 2, 3, 4, "]"])
