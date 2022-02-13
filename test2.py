from exceldb.parser.pattern_matching import *

x = Anchor[
    "list",
    Expression[
        NonCaptureGroup["["],
        CaptureGroup[ZeroOrOne[OneOrMany[Choice[Instance[int], Reference["list"]]]]],
        NonCaptureGroup["]"],
    ],
]

print(x(["[", 1, "[", 2, 4, 5, "]", 3, 4, "]"]))
