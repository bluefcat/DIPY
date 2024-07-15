import pytest
from pyparsing import ParserElement
from dice.dice.element import *

TESTCOUNT = 1000


import sys
sys.setrecursionlimit(15000)

def split_oper(operator):
    return operator.operands[0], operator.operands[1]

def split_pair(pair):
    return pair.values[0], pair.values[1]


@pytest.mark.asyncio
async def test_normal_single_number(
    expr: ParserElement,
    normal_single_number: str
):
    result = expr.parse_string(normal_single_number, parse_all=True)
    result = result[0]
    assert result == 6 

@pytest.mark.asyncio
async def test_normal_single_calc(
    expr: ParserElement,
    normal_single_calc: str
):
    result = expr.parse_string(normal_single_calc, parse_all=True)[0]

    assert isinstance(result, Add) 
    x, y = split_oper(result)
    assert x == 4

    assert isinstance(y, Mul)
    w, z = split_oper(y)
    assert w == 2 and z == 3

@pytest.mark.asyncio
async def test_normal_single_dice(
    expr: ParserElement,
    normal_single_dice: str
):
    result = expr.parse_string(normal_single_dice, parse_all=True)[0]
    
    assert isinstance(result, Dice)
    x, y = split_oper(result)
    assert x == 3 and y == 6

@pytest.mark.asyncio
async def test_normal_braket_dice(
    expr: ParserElement,
    normal_braket_dice: str
):
    result = expr.parse_string(normal_braket_dice, parse_all=True)[0]

    assert isinstance(result, Dice)
    x, y = split_oper(result)
    assert x == 3

    assert isinstance(y, Dice)
    w, z = split_oper(y)
    assert w == 1 and z == 6

@pytest.mark.asyncio
async def test_normal_combine_dice(
    expr: ParserElement,
    normal_combine_dice: str
):
    result = expr.parse_string(normal_combine_dice, parse_all=True)[0]

    assert isinstance(result, Repeat)
    x, y = split_oper(result)
    assert x == 3

    assert isinstance(y, Dice)
    w, z = split_oper(y)
    assert w == 2 and z == 6


@pytest.mark.asyncio
async def test_normal_minimum_dice(
    expr: ParserElement,
    normal_minmum_dice: str
):
    result = expr.parse_string(normal_minmum_dice, parse_all=True)[0]

    assert isinstance(result, Dice)
    x, y = split_oper(result)
    assert x == 1

    assert isinstance(y, Pair)
    w, z = split_pair(y)
    assert w == 10 and z == 20

@pytest.mark.asyncio
async def test_normal_max_kn_dice(
    expr: ParserElement,
    normal_max_kn_dice: str
):
    result = expr.parse_string(normal_max_kn_dice, parse_all=True)[0] 
    assert isinstance(result, KeepMax)
    x, y = split_oper(result)
    assert y == 2

    assert isinstance(x, Dice)
    w, z = split_oper(x)
    assert w == 3 and z == 6

@pytest.mark.asyncio
async def test_normal_min_kn_dice(
    expr: ParserElement,
    normal_min_kn_dice: str
):
    result = expr.parse_string(normal_min_kn_dice, parse_all=True)[0] 
    assert isinstance(result, KeepMin)
    x, y = split_oper(result)
    assert y == 2

    assert isinstance(x, Dice)
    w, z = split_oper(x)
    assert w == 3 and z == 6


@pytest.mark.asyncio
async def test_normal_gt_dice(
    expr: ParserElement,
    normal_gt_dice: str
):
    result = expr.parse_string(normal_gt_dice, parse_all=True)[0]
    assert isinstance(result, GT)
    x, y = split_oper(result)
    assert y == 0

    assert isinstance(x, Dice)
    w, z = split_oper(x)
    assert w == 1 and z == 6

@pytest.mark.asyncio
async def test_normal_lt_dice(
    expr: ParserElement,
    normal_lt_dice: str
):
    result = expr.parse_string(normal_lt_dice, parse_all=True)[0]
    assert isinstance(result, LT)
    x, y = split_oper(result)
    assert y == 0

    assert isinstance(x, Dice)
    w, z = split_oper(x)
    assert w == 1 and z == 6

@pytest.mark.asyncio
async def test_normal_ge_dice(
    expr: ParserElement,
    normal_ge_dice: str
):
    result = expr.parse_string(normal_ge_dice, parse_all=True)[0]
    assert isinstance(result, GE)
    x, y = split_oper(result)
    assert y == 1

    assert isinstance(x, Dice)
    w, z = split_oper(x)
    assert w == 1 and z == 6

@pytest.mark.asyncio
async def test_normal_le_dice(
    expr: ParserElement,
    normal_le_dice: str
):
    result = expr.parse_string(normal_le_dice, parse_all=True)[0]
    assert isinstance(result, LE)
    x, y = split_oper(result)
    assert y == 1

    assert isinstance(x, Dice)
    w, z = split_oper(x)
    assert w == 1 and z == 6

@pytest.mark.asyncio
async def test_normal_eq_dice(
    expr: ParserElement,
    normal_eq_dice: str
):
    result = expr.parse_string(normal_eq_dice, parse_all=True)[0]
    assert isinstance(result, EQ)
    x, y = split_oper(result)
    assert y == 6

    assert isinstance(x, Dice)
    w, z = split_oper(x)
    assert w == 1 
    
    assert isinstance(z, Pair)
    a, b = split_pair(z)
    assert a == 6 and b == 6

@pytest.mark.asyncio
async def test_normal_ne_dice(
    expr: ParserElement,
    normal_ne_dice: str
):
    result = expr.parse_string(normal_ne_dice, parse_all=True)[0]
    assert isinstance(result, NE)
    x, y = split_oper(result)
    assert y == 0

    assert isinstance(x, Dice)
    w, z = split_oper(x)
    assert w == 1 and z == 6
