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
)
from .pattern_matching import Expression, Instance, OneOrMany, ZeroOrOne, Choice
from .pattern_matching import CaptureGroup as CG
from .pattern_matching import NonCaptureGroup as NCG

_DT = Choice[
    Expression[
        Choice[DT("CHAR"), DT("VARCHAR")],
        NCG[CTX("(")],
        Instance[VAL],
        NCG[CTX(")")],
    ],
    Instance[DT],
]

_CSV = lambda x: Expression[x, ZeroOrOne[OneOrMany[NCG[CTX(",")], x]]]
_ARRAY = lambda x: Expression[NCG[CTX("(")], _CSV(x), NCG[CTX(")")]]
_BOOL = Expression[
    Choice[
        Expression[
            Instance[NAME], AOPR("BETWEEN"), Instance[VAL], BOPR("AND"), Instance[VAL]
        ],
        Expression[Instance[NAME], AOPR("LIKE"), Instance[VAL]],
        Expression[
            Instance[NAME],
            AOPR("IN"),
            _ARRAY(Instance[VAL]),
        ],
        Expression[Instance[NAME], Instance[SOPR], Instance[VAL]],
    ]
]

BOOL = Expression[
    CG[ZeroOrOne[Expression[BOPR("NOT")]], _BOOL],
    ZeroOrOne[
        OneOrMany[
            CG[Choice[Expression[BOPR("AND")], Expression[BOPR("OR")]]],
            CG[ZeroOrOne[Expression[BOPR("NOT")]], _BOOL],
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
