from typing import List
from pyparsing import (
    Forward,
    ParserElement,
    StringStart,
    StringEnd,
    Suppress,
    Word, nums
)

from dice.dice.association import Association
from dice.dice.element import *

__all__ = ["expression"]

def build_expression(
    base: Word,
    pair: Association,
    associations: List[Association]
) -> ParserElement:
    expression = Forward()
    last = (
        base | 
        pair.get_expression(expression) |
        Suppress("(") + expression + Suppress(")")
    )

    for association in associations:
        last = association.get_expression(last)

    expression <<= last
    return expression

integer: Word = Word(nums)
integer.set_parse_action(Integer.parse)

expression: ParserElement = (
    StringStart() 
    + build_expression(
        integer, Pair, # type: ignore
        # The order of this list determines operator precedence.
        [              # type: ignore 
            Dice, SingleDice, Repeat, KeepMax, KeepMin, 
            Neg, Div, Mul, Sub, Add, 
            GE, GT, LE, LT, EQ, NE, 
        ]
    )
    + StringEnd()
)
expression.enable_packrat()

