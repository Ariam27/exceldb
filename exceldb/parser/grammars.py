from .tokens import (
    DDL,
    DML,
    EOF,
    TCL,
    DQL,
    HL,
    DT,
    SOPR,
    AOPR,
    BOPR,
    CTX,
    EOL,
    NAME,
    VAL,
    INTVAL,
)
from .pattern_matching import (
    Expression,
    Instance,
    OneOrMany,
    ZeroOrOne,
    Choice,
    Not,
    Anchor,
    Reference,
)
from .pattern_matching import CaptureGroup as CG
from .pattern_matching import NonCaptureGroup as NCG

PATTERN = CG[
    ZeroOrOne[
        Anchor[
            "wildcard",
            OneOrMany[
                Choice[
                    CG[Choice["_", "%"]],
                    CG["[", Instance[str], "-", Instance[str], "]"],
                    CG[
                        "[",
                        OneOrMany[
                            Choice[
                                Expression[NCG["\\"], "\\"],
                                Expression[NCG["\\"], "]"],
                                Not["]"],
                            ]
                        ],
                        "]",
                    ],
                ]
            ],
        ]
    ],
    ZeroOrOne[
        OneOrMany[
            Choice[
                CG["\\", Choice["b", "r", "n", "t"]],
                Expression[NCG["\\"], "\\"],
                Expression[Not["\\"], Reference["wildcard"]],
                NCG["\\"],
                Instance[str],
            ]
        ]
    ],
]


_DT = Choice[
    Expression[
        Choice[DT("CHAR"), DT("VARCHAR")],
        NCG[CTX("(")],
        Instance[INTVAL],
        NCG[CTX(")")],
    ],
    Instance[DT],
]

_CSV = lambda x: Expression[x, ZeroOrOne[OneOrMany[NCG[CTX(",")], x]]]
_ARRAY = lambda x: Expression[NCG[CTX("(")], _CSV(x), NCG[CTX(")")]]
_BOOL = Expression[
    Choice[
        Expression[
            Instance[NAME],
            ZeroOrOne[BOPR("NOT")],
            AOPR("BETWEEN"),
            Instance[VAL],
            NCG[BOPR("AND")],
            Instance[VAL],
        ],
        Expression[Instance[NAME], ZeroOrOne[BOPR("NOT")], AOPR("LIKE"), Instance[VAL]],
        Expression[
            Instance[NAME],
            ZeroOrOne[BOPR("NOT")],
            AOPR("IN"),
            _ARRAY(Instance[VAL]),
        ],
        Expression[
            ZeroOrOne[BOPR("NOT")], Instance[NAME], Instance[SOPR], Instance[VAL]
        ],
    ]
]

BOOL = Anchor[
    "bool",
    CG[
        Choice[
            _BOOL,
            Expression[
                ZeroOrOne[BOPR("NOT")], NCG[CTX("(")], Reference["bool"], NCG[CTX(")")]
            ],
        ],
    ],
    ZeroOrOne[
        OneOrMany[
            CG[Choice[Expression[BOPR("AND")], Expression[BOPR("OR")]]],
            CG[
                Choice[
                    _BOOL,
                    Expression[NCG[CTX("(")], Reference["bool"], NCG[CTX(")")]],
                ],
            ],
        ]
    ],
]

SELECT = Expression[
    CG[DQL("SELECT")],
    CG[_CSV(Instance[NAME])],
    NCG[HL("FROM")],
    CG[Instance[NAME]],
    CG[ZeroOrOne[NCG[HL("WHERE")], BOOL]],
    NCG[EOL(";")],
]

INSERT = Expression[
    CG[DML("INSERT")],
    NCG[HL("INTO")],
    CG[Instance[NAME]],
    CG[ZeroOrOne[_ARRAY(Instance[NAME])]],
    NCG[HL("VALUES")],
    CG[_ARRAY(Instance[VAL])],
    NCG[EOL(";")],
]

UPDATE = Expression[
    CG[DML("UPDATE")],
    CG[Instance[NAME]],
    NCG[HL("SET")],
    CG[_CSV(CG[Instance[NAME], SOPR("="), Instance[VAL]])],
    CG[ZeroOrOne[NCG[HL("WHERE")], BOOL]],
    NCG[EOL(";")],
]

DELETE = Expression[
    CG[DML("DELETE")],
    NCG[HL("FROM")],
    CG[Instance[NAME]],
    CG[ZeroOrOne[NCG[HL("WHERE")], BOOL]],
    NCG[EOL(";")],
]

USE = Expression[
    CG[DDL("USE")], CG[Choice[Instance[NAME], Instance[VAL]]], NCG[EOL(";")]
]

CREATE = Choice[
    Expression[
        CG[DDL("CREATE")], CG[HL("DATABASE")], CG[Instance[NAME]], NCG[EOL(";")]
    ],
    Expression[
        CG[DDL("CREATE")],
        CG[HL("TABLE")],
        CG[Instance[NAME]],
        CG[_ARRAY(CG[Instance[NAME], _DT])],
        NCG[EOL(";")],
    ],
    Expression[
        CG[DDL("CREATE")],
        CG[HL("TABLE")],
        CG[Instance[NAME]],
        NCG[HL("AS")],
        CG[DQL("SELECT")],
        CG[_CSV(Instance[NAME])],
        NCG[HL("FROM")],
        CG[Instance[NAME]],
        CG[ZeroOrOne[NCG[HL("WHERE")], BOOL]],
        NCG[EOL(";")],
    ],
]

DROP = Choice[
    Expression[CG[DDL("DROP")], CG[HL("DATABASE")], CG[Instance[NAME]], NCG[EOL(";")]],
    Expression[CG[DDL("DROP")], CG[HL("TABLE")], CG[Instance[NAME]], NCG[EOL(";")]],
]

TRUNCATE = Expression[
    CG[DDL("TRUNCATE")], CG[HL("TABLE")], CG[Instance[NAME]], NCG[EOL(";")]
]

ALTER = Expression[
    CG[DDL("ALTER")],
    CG[HL("TABLE")],
    CG[Instance[NAME]],
    Choice[
        Expression[CG[DDL("DROP")], NCG[HL("COLUMN")], CG[Instance[NAME]]],
        Expression[CG[HL("MODIFY")], NCG[HL("COLUMN")], CG[Instance[NAME]], CG[_DT]],
        Expression[CG[HL("ADD")], CG[Instance[NAME]], CG[_DT]],
    ],
    NCG[EOL(";")],
]

COMMIT = Expression[CG[TCL("COMMIT")], NCG[EOL(";")]]

ROLLBACK = Expression[CG[TCL("ROLLBACK")], NCG[EOL(";")]]

STATEMENT = Expression[
    OneOrMany[
        CG[
            Choice[
                SELECT,
                INSERT,
                UPDATE,
                DELETE,
                USE,
                CREATE,
                DROP,
                TRUNCATE,
                ALTER,
                COMMIT,
                ROLLBACK,
            ]
        ]
    ],
    EOF("EOF"),
]
