from enum import Enum


class DDL(Enum):
    USE = "USE"
    CREATE = "CREATE"
    DROP = "DROP"
    ALTER = "ALTER"
    TRUNCATE = "TRUNCATE"


class DML(Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class TCL(Enum):
    COMMIT = "COMMIT"
    ROLLBACK = "ROLLBACK"


class DQL(Enum):
    SELECT = "SELECT"


class HL(Enum):
    TABLE = "TABLE"
    DATABASE = "DATABASE"
    COLUMN = "COLUMN"
    AS = "AS"
    ADD = "ADD"
    MODIFY = "MODIFY"
    INTO = "INTO"
    VALUES = "VALUES"
    SET = "SET"
    FROM = "FROM"
    WHERE = "WHERE"


class DT(Enum):
    CHAR = "CHAR"
    VARCHAR = "VARCHAR"
    TEXT = "TEXT"
    INT = "INT"
    FLOAT = "FLOAT"
    DATETIME = "DATETIME"
    DATE = "DATE"
    TIME = "TIME"


class AOPR(Enum):
    BETWEEN = "BETWEEN"
    LIKE = "LIKE"
    IN = "IN"


class SOPR(Enum):
    EQ = "="
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="
    NEQ = "!="


class BOPR(Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class CTX(Enum):
    OPN = "("
    CPN = ")"
    SEP = ","


class END(Enum):
    EOF = "EOF"
    EOL = ";"


class IGN(Enum):
    WHS = " "
    NL = "\n"
