import csv
import os
from parser import lexer, tokens, grammars

path = ""
tables = []
headers = {}
data = {}


def NAME(value):
    return isinstance(lexer.Lexer(value).tokens[0], tokens.NAME)


def DATATYPE(value):
    return grammars._DT == lexer.Lexer(value).tokens[:-1]


def WHERE(statement, table):
    print(statement)


def SELECT(statement):
    columns = [i.token for i in statement[1]]
    table = statement[2][0].token
    if "*" in columns and len(columns) > 1:
        raise ValueError(f"Columns '{', '.join(columns)}' are not defined")
    if columns[0] != "*":
        for column in columns:
            if not column in headers[table].keys():
                raise ValueError(f"Column '{column}' is not defined")
    columns = headers[table].keys() if columns[0] == "*" else columns

    filtered = WHERE(statement[3], table)


def INSERT(statement):
    pass


def UPDATE(statement):
    pass


def DELETE(statement):
    pass


def USE(statement):
    _path = statement[1][0].token
    _path = _path if _path.startswith("/") else os.path.join(os.getcwd(), _path)

    if os.path.exists(_path):
        if os.path.exists(os.path.join(_path, "tables")):
            with open(os.path.join(_path, "tables"), "r") as _tables:
                tables = next(csv.reader(_tables, delimiter=","))

            for table in tables:
                with open(os.path.join(_path, table + ".csv")) as _table:
                    reader = csv.reader(_table, delimiter=",")
                    col_names = next(reader)
                    for name in col_names:
                        if not NAME(name):
                            raise ValueError(
                                f"Column Name '{name}' in Table '{table}' is not valid"
                            )

                    col_types = next(reader)
                    for type in col_types:
                        if not DATATYPE(type):
                            raise ValueError(
                                f"Data Type '{type}' in Table '{table}' is not valid"
                            )

                    headers[table] = {
                        name: type for name, type in zip(col_names, col_types)
                    }
                    data[table] = list(reader)
                    return
        raise FileNotFoundError(f"'tables' file for directory '{_path}' does not exist")
    raise FileNotFoundError(f"No such directory: {_path}")


def CREATE(statement):
    pass


def DROP(statement):
    pass


def TRUNCATE(statement):
    pass


def ALTER(statement):
    pass


def COMMIT(statement):
    pass


def ROLLBACK(statement):
    pass


statement_map = {
    "SELECT": SELECT,
    "INSERT": INSERT,
    "UPDATE": UPDATE,
    "DELETE": DELETE,
    "USE": USE,
    "CREATE": CREATE,
    "DROP": DROP,
    "TRUNCATE": TRUNCATE,
    "ALTER": ALTER,
    "COMMIT": COMMIT,
    "ROLLBACK": ROLLBACK,
}


def execute(tree):
    for statement in tree:
        result = statement_map[statement[0][0].token](statement)
    return tree
