from dataclasses import dataclass, field
from typing import Literal, Union
from . import enums


@dataclass
class Token:
    token: str


@dataclass
class NAME(Token):
    token: str
    original: str = field(default=None, repr=False, compare=False)


@dataclass
class VAL(Token):
    token: Union[float, str]


@dataclass
class INTVAL(VAL):
    token: int


@dataclass
class UKN(Token):
    token: str


@dataclass
class DDL(NAME):
    token: enums.DDL


@dataclass
class DML(NAME):
    token: enums.DML


@dataclass
class TCL(NAME):
    token: enums.TCL


@dataclass
class DQL(NAME):
    token: enums.DQL


@dataclass
class HL(NAME):
    token: enums.HL


@dataclass
class DT(NAME):
    token: enums.DT


@dataclass
class BOPR(NAME):
    token: enums.BOPR


@dataclass
class AOPR(NAME):
    token: enums.AOPR


@dataclass
class SOPR(Token):
    token: enums.SOPR


@dataclass
class CTX(Token):
    token: enums.CTX


@dataclass
class EOL(Token):
    token: Literal[";"]


@dataclass
class EOF(Token):
    token: Literal["EOF"]
