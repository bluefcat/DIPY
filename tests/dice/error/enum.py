from enum import Enum

class Error(Enum):
    AssertionError = "assertion error"
    IndexError = "index error"
    ValueError = "value error"
    TypeError = "syntax error"
    ZeroDivisionError = "zero division"

    HTTPException = "too long message"
    ParseException = "parse error"

    RangeException = "range error"
    ShapeException = "shape must be integer, integer list or pair"

    ShapeOverException = f"shape over"
    AmountOverException = f"count over"
