__all__ = [
    "RangeException",
    "ShapeException",
    "ShapeOverException",
    "AmountOverException",
]

class RangeException(Exception):
    ...

class ShapeException(Exception):
    ...

class ShapeOverException(Exception):
    ...

class AmountOverException(Exception):
    ...

