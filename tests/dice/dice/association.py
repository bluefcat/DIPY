from abc import ABC, abstractmethod
from typing import List
from pyparsing import (
    ParserElement,
    OneOrMore,
    Forward,
    Suppress,
)

class Association(ABC):
    symbols: List[ParserElement] = []
    extra = None
    @classmethod
    def parse(cls, tokens):
        return cls(*tokens)
     
    @classmethod
    @abstractmethod
    def get_expression(cls, last: ParserElement) -> ParserElement:
        ...

class SingleAssociation(Association):
    @classmethod
    def get_expression(cls, last: ParserElement) -> ParserElement:
        return last

class PairAssociation(Association):
    @classmethod
    def get_expression(cls, last: ParserElement) ->ParserElement:
        left, right = cls.symbols
        expr = left+last+Suppress(",")+last+right
        expr.set_parse_action(cls.parse)

        return expr

class RightUnaryAssociation(Association):
    @classmethod
    def get_expression(cls, last: ParserElement) -> ParserElement:
        this = Forward()
        new_this = (this | cls.extra) if cls.extra else this
        
        symbol = cls.symbols[0]
        for s in cls.symbols[1:]:
            symbol |= s

        expr = symbol + new_this
        expr.set_parse_action(cls.parse)
        
        this <<= expr | last
        last = this
        return last

class LeftBinaryAssociation(Association):
    @classmethod
    def get_expression(cls, last: ParserElement) -> ParserElement:
        this: ParserElement = Forward()
        expr: ParserElement = Forward()
        new_last = (last | cls.extra) if cls.extra else last
        
        symbol = cls.symbols[0]
        for s in cls.symbols[1:]:
            symbol |= s

        expr = last + OneOrMore(symbol + new_last)
        expr.set_parse_action(cls.parse)

        this <<= expr | last
        last = this
        return last

