import csv
import os
from datetime import datetime as dt
from parser import lexer, tokens, grammars
from parser import pattern_matching as pm


class CISlist(list):
    def index(self, item):
        return [i.lower() for i in self].index(item.lower())

    def __contains__(self, item):
        return item.lower() in [i.lower() for i in self]


class CISdict(dict):
    def keys(self):
        return CISlist(super().keys())

    def __getitem__(self, key):
        return list(self.values())[self.keys().index(key)]


_index = lambda val, array: [i for i in range(len(array)) if val == array[i]]

path = ""
tables = CISlist([])
headers = CISdict({})
data = CISdict({})


def NAME(value):
    return isinstance(lexer.Lexer(value).tokens[0], tokens.NAME)


def DATATYPE(value):
    return grammars._DT == lexer.Lexer(value).tokens[:-1]


def CHECK(datatype):
    pass


def BOOL(statement, table):
    def CONVERT(datatype):
        datatype_map = {
            "TEXT": str,
            "INT": int,
            "FLOAT": float,
            "DATETIME": lambda val: dt.strptime(val, "%Y-%m-%d %H:%M:%S"),
            "DATE": lambda val: dt.strptime(val, "%Y-%m-%d"),
            "TIME": lambda val: dt.strptime(val, "%H:%M:%S"),
        }

        if datatype.startswith("CHAR") or datatype.startswith("VARCHAR"):
            return datatype_map["TEXT"]
        return datatype_map[datatype]

    def BETWEEN(statement):
        column = statement[0].original
        index = columns.index(column)
        _convert = CONVERT(headers[table][column][0])

        try:
            compare = [_convert(statement[i].token) for i in (2, 3)]
        except (TypeError, ValueError):
            return lambda row: False

        def _filter(row):
            value = _convert(row[index])
            return value >= compare[0] and value <= compare[1]

        return _filter

    def LIKE(statement):
        column = statement[0].original
        index = columns.index(column)
        pattern = grammars.PATTERN(str(statement[2].token))[0]

        if pattern == []:
            pattern = [""]

        terms = []
        for term in pattern:
            if isinstance(term, list):
                escape_map = {"b": "\b", "r": "\r", "n": "\n", "t": "\t"}

                if term[0] == "_":
                    terms.append(pm.Instance[str])
                    continue

                if term[0] == "%":
                    terms.append(pm.ZeroOrOne[pm.OneOrMany[pm.Instance[str]]])
                    continue

                if term[0] == "//":
                    terms.append(escape_map[term[1]])
                    continue

                if term[0] == "[" and term[-1] == "]":
                    if len(term) == 5 and term[2] == "-":
                        exp = pm._Choice(
                            [chr(i) for i in range(ord(term[1]), ord(term[3]) + 1)]
                        )
                        terms.append(exp)
                        continue

                    _charlist = term[1:-1]
                    _not = True if _charlist[0] == "^" else False
                    if _not:
                        del _charlist[0]

                    charlist = set()
                    i = 0
                    while i < len(_charlist):
                        if _charlist[i] == "\\":
                            seq = (
                                escape_map.get(_charlist[i + 1])
                                if i + 1 != len(_charlist)
                                else None
                            )
                            if seq:
                                charlist.add(seq)
                                i += 2
                                continue
                        charlist.add(_charlist[i])
                        i += 1

                    exp = pm._Choice(list(charlist))
                    terms.append(pm.Not[exp] if _not else exp)
                    continue

            terms.append(term)
        _pattern = pm._Expression(terms)

        def _filter(row):
            return _pattern == str(row[index])

        return _filter

    def IN(statement):
        column = statement[0].original
        index = columns.index(column)
        _convert = CONVERT(headers[table][column][0])
        compare = []

        for item in statement[2]:
            try:
                compare.append(_convert(item.token))
            except (TypeError, ValueError):
                compare.append(item)

        def _filter(row):
            value = _convert(row[index])
            return value in compare

        return _filter

    def SOPR(statement):
        SOPR_map = {
            "=": lambda x, y: x == y,
            ">": lambda x, y: x > y,
            "<": lambda x, y: x < y,
            ">=": lambda x, y: x >= y,
            "<=": lambda x, y: x <= y,
            "!=": lambda x, y: x != y,
        }

        column = statement[0].original
        index = columns.index(column)
        _convert = CONVERT(headers[table][column][0])
        _func = SOPR_map[statement[1].token]

        try:
            compare = _convert(statement[2].token)
        except (TypeError, ValueError):
            return lambda row: False

        def _filter(row):
            value = _convert(row[index])
            return _func(value, compare)

        return _filter

    def AND(statement):
        _filters = [
            statement[i] if callable(statement[i]) else BOOL(statement[i], table)
            for i in [0, 2]
        ]
        return lambda row: _filters[0](row) and _filters[1](row)

    def OR(statement):
        _filters = [
            statement[i] if callable(statement[i]) else BOOL(statement[i], table)
            for i in [0, 2]
        ]
        return lambda row: _filters[0](row) or _filters[1](row)

    def NOT(statement):
        _filter = BOOL([i for i in statement if i != tokens.BOPR("NOT")], table)
        return lambda row: not _filter(row)

    excavate = (
        lambda array: excavate(array[0])
        if len(array) == 1 and isinstance(array[0], list)
        else array
    )
    statement = excavate(statement)

    indices_and = _index([tokens.BOPR("AND")], statement)
    indices_or = _index([tokens.BOPR("OR")], statement)

    if indices_and != [] or indices_or != []:
        for i in indices_and:
            statement[i - 1 : i + 2] = [AND(statement[i - 1 : i + 2])]

        for i in indices_or:
            statement[i - 1 : i + 2] = [OR(statement[i - 1 : i + 2])]

        return statement[0]

    if tokens.BOPR("NOT") in statement:
        return NOT(statement)

    columns = headers[table].keys()
    if not statement[0].original in columns:
        raise ValueError(f"Column '{statement[0].original}' is not defined")

    AOPR_map = {
        "BETWEEN": BETWEEN,
        "LIKE": LIKE,
        "IN": IN,
    }
    val = AOPR_map.get(statement[1].token)

    if val:
        return val(statement)

    return SOPR(statement)


def WHERE(statement, table):
    if statement == []:
        return data[table]

    _filter = BOOL(statement, table)
    return [row for row in data[table] if _filter(row)]


def SELECT(statement):
    columns = CISlist([i.original for i in statement[1]])
    table = statement[2][0].original
    cols = headers[table].keys()
    if "*" in columns and len(columns) > 1:
        raise ValueError(f"Columns '{', '.join(columns)}' are not defined")
    if columns[0] != "*":
        for column in columns:
            if not column in cols:
                raise ValueError(f"Column '{column}' is not defined")
    columns = cols if columns[0] == "*" else columns

    filtered = WHERE(statement[3], table)

    if columns == cols:
        return filtered

    indices = [cols.index(column) for column in columns]

    def _sort(row):
        return [row[i] for i in indices]

    return [_sort(row) for row in filtered]


def INSERT(statement):
    pass


def UPDATE(statement):
    pass


def DELETE(statement):
    pass


def USE(statement):
    _path = (
        statement[1][0].token
        if isinstance(statement[1][0], tokens.VAL)
        else statement[1][0].original
    )
    _path = _path if _path.startswith("/") else os.path.join(os.getcwd(), _path)

    if os.path.exists(_path):
        if os.path.exists(os.path.join(_path, "tables")):
            with open(os.path.join(_path, "tables"), "r") as _tables:
                tables = CISlist(next(csv.reader(_tables, delimiter=",")))

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

                    headers[table] = CISdict(
                        {
                            name: (type.upper(), CHECK(type.upper()))
                            for name, type in zip(col_names, col_types)
                        }
                    )
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
    return result
