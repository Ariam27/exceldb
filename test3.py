from click import BadParameter
from exceldb.parser.tokens import *

statement = [BOPR("AND"), BOPR("OR"), BOPR("NOT"), BOPR("AND")]
find_all = lambda val, l: [i for i in range(len(l)) if val == l[i]]

print(find_all(BOPR("AND"), statement))
