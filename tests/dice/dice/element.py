import operator
import random
from typing import (
    Any, List, Callable, Union, Dict,
)
from pyparsing import Literal, Suppress

from dice.error.custom import *
from dice.dice.association import (
    SingleAssociation,
    PairAssociation,
    RightUnaryAssociation,
    LeftBinaryAssociation
)

from dice.dice.recorder import record, recorder

__all__ = [
    "Integer",
    "String",
    "IntegerList",
    "Pair",
    "Repeat",
    "Dice",
    "SingleDice",
    "Neg",
    "Add",
    "Sub",
    "Mul",
    "Div",
    "GE",
    "LE",
    "GT",
    "LT",
    "EQ",
    "NE",
    "KeepMax",
    "KeepMin",
]

Intable = Union["Integer", "IntegerList"]


MAXSHAPE  = 10000
MAXAMOUNT = 10000

class Base:
    """
    All element must inherit Base class
    """
    def __init__(self, *_, **__):
        self.outcome: Dict[str, "Base"] = {"result": self}

    @property
    def name(self) -> str:
        """
        class name 
        return:
            str
        ex) Base().name -> "Base"
        """
        return self.__class__.__name__

    def evaluate(self, tid: int = -1) -> "Base":
        """
        Evaluate element
        return:
            Base
        ex) Dice(2, 3).evaluate(tid) -> 2d3
        """
        return self

class Integer(int, Base, SingleAssociation):
    """int wrapper class"""
    ...

class String(str, Base, SingleAssociation):
    """str wrapper class"""
    ...


class IntegerList(List[Integer], Base, SingleAssociation): 
    """List[Base] wrapper class"""
    def __int__(self) -> int:
        """
        return:
            sum of elements
        """
        return sum(self)

class Pair(Base, PairAssociation):
    """Pair is expression for (min, max)"""
    symbols=[Suppress("("), Suppress(")")]

    def __init__(self, *value: Any):
        super().__init__()
        self.values: List[Base] = list(value) 
        self.record: str = ""

    def __repr__(self) -> str:
        args = ", ".join(
            map(str, self.values)
        ) 
        return f"({args})" 

    def __getitem__(self, idx: int) -> Base:
        return self.values[idx]
    
    def evaluate(self, tid: int = -1) -> "Pair":
        """
        return:
            Pair: Return a pair of the evaluation of each element.
        """
        values = IntegerList()
        for value in self.values:
            r = value.evaluate(tid)
            assert isinstance(r, Integer | IntegerList)
            values.append(
                Integer(int(r))
            )

        if values[0] > values[1]:
            raise RangeException()

        self.outcome["result"] = Pair(*values)
        return self.outcome["result"] 

class Repeat(Base, LeftBinaryAssociation):
    """Repeat is repeating evaluable functions"""
    symbols = [
        Literal("N").suppress(),
        Literal("n").suppress(),
    ]

    def __init__(self, *operands: Any):
        super().__init__()
        self.operands: List[Base] = list(operands)

    def __repr__(self) -> str:
        args = ", ".join(
            map(str, self.operands)
        )
        return f"{self.name}({args})"
    
    @record(recorder, "repeat result -> {result} **{sum}**")
    def evaluate(self, tid: int = -1) -> IntegerList:
        amount, evaluable = self.operands
        amount = amount.evaluate(tid)
        assert isinstance(amount, Integer | IntegerList)
        if int(amount) >= MAXAMOUNT:
            raise AmountOverException()

        result = IntegerList()
        
        for _ in range(int(amount)):
            tmp = evaluable.evaluate(tid)
            assert isinstance(tmp, Integer | IntegerList)
            result.append(Integer(int(tmp)))
        
        self.outcome.update(
            {
                "result": result,
                "sum": Integer(int(result))
            }
        )

        return result

class Operator(Base):
    def __init__(self, *operands: Any):
        super().__init__()
        self.operands: List[Base] = list(operands)
        
    def __repr__(self) -> str:
        args = ", ".join(
            map(str, self.operands)
        )
        return f"{self.name}({args})"
    
    def evaluate(self, tid: int = -1) -> Base:
        operands: List = [
            operand.evaluate(tid) for operand in self.operands
        ]
        try:
            value = self.function(*operands)
        except TypeError:
            value = operands[0]
            for operand in operands[1:]:
                value = self.function(value, operand)
        
        self.outcome["result"] = value 
        return self.outcome["result"]

    @property
    def function(self) -> Callable[..., Base]:
        raise NotImplementedError(
            f"{self.name} operator is not implemented function"
        )

class Dice(Operator, LeftBinaryAssociation):
    symbols = [
        Literal("d").suppress(),
        Literal("D").suppress(),
    ]

    @record(recorder, "{amount}d{shape} -> {result} **{sum}**")
    def evaluate(self, tid: int = -1) -> Base:
        result = super().evaluate(tid)
        amount = self.operands[0].outcome["result"] 
        shape = self.operands[1].outcome["result"]
        
        if isinstance(amount, Integer | IntegerList):
            amount = Integer(int(amount))

        if isinstance(shape, Integer | IntegerList):
            shape = Integer(int(shape))
        
        if isinstance(amount, Integer) and amount >= MAXAMOUNT:
            raise AmountOverException()
        
        if isinstance(shape, Integer) and shape >= MAXSHAPE:
            raise ShapeOverException()
        
        if isinstance(shape, Pair) and shape[1] >= MAXSHAPE:
            raise ShapeOverException()
        assert isinstance(result, Integer | IntegerList)
        self.outcome.update({
            "amount": amount,
            "shape": shape,
            "sum": Integer(int(result))
        })

        return result 

    @property
    def function(self) -> Callable[..., Base]:
        def f(
            amount: Intable, 
            shape: Union[Integer, Pair]
        ) -> IntegerList:
            min_value, max_value = (Integer(1), shape)
            if isinstance(shape, Pair):
                min_value, max_value = (shape)
            assert isinstance(min_value, Integer | IntegerList)
            assert isinstance(max_value, Integer | IntegerList) 
            return IntegerList(
                Integer(random.randint(int(min_value), int(max_value)))
                for _ in range(int(amount))
            )
        return f 

class SingleDice(Operator, RightUnaryAssociation):
    symbols = [
        Literal("d").suppress(),
        Literal("D").suppress(),
    ]
    @record(recorder, "{amount}d{shape} -> {result} **{sum}**")
    def evaluate(self, tid: int = -1) -> Base:
        result = super().evaluate(tid)
        amount = Integer(1)
        shape = self.operands[0].outcome["result"]
        
        if isinstance(amount, Integer | IntegerList):
            amount = Integer(int(amount))

        if isinstance(shape, Integer | IntegerList):
            shape = Integer(int(shape))
        
        if isinstance(shape, Integer) and shape >= MAXSHAPE:
            raise ShapeOverException()
        
        if isinstance(shape, Pair) and shape[1] >= MAXSHAPE:
            raise ShapeOverException()

        assert isinstance(result, Integer | IntegerList)
        self.outcome.update({
            "amount": amount,
            "shape": shape,
            "sum": Integer(int(result))
        })

        return result 

    @property
    def function(self) -> Callable[..., Base]:
        def f(
            shape: Union[Integer, Pair]
        ) -> IntegerList:
            min_value, max_value = (Integer(1), shape)
            if isinstance(shape, Pair):
                min_value, max_value = (shape)
            
            assert isinstance(min_value, Integer | IntegerList)
            assert isinstance(max_value, Integer | IntegerList) 
            return IntegerList(
                Integer(random.randint(int(min_value), int(max_value)))
                for _ in range(1)
            )
        return f 


class Neg(Operator, RightUnaryAssociation):
    symbols = [Literal("-").suppress()]
    @property
    def function(self) -> Callable[..., Base]:
        def f(x: Intable) -> Intable:
            if isinstance(x, Integer):
                return Integer(
                    operator.neg(x)
                )

            return IntegerList(
                [Integer(operator.neg(k)) for k in x]
            )

        return f

class Add(Operator, LeftBinaryAssociation):
    symbols = [Literal("+").suppress()]
    @property
    def function(self) -> Callable[..., Base]:
        def f(
			x: Intable,
			y: Intable
		) -> Integer:
            return Integer(
                operator.add(int(x), int(y))
            )
        return f 

class Sub(Operator, LeftBinaryAssociation):
    symbols = [Literal("-").suppress()]
    @property
    def function(self) -> Callable[..., Base]:
        def f(
			x: Intable,
			y: Intable
		) -> Integer:
            return Integer(
                operator.sub(int(x), int(y))
            )
        return f 

class Mul(Operator, LeftBinaryAssociation):
    symbols = [Literal("*").suppress()]
    @property
    def function(self) -> Callable[..., Base]:
        def f(
			x: Intable,
			y: Intable
		) -> Integer:
            return Integer(
                operator.mul(int(x), int(y))
            )
        return f 

class Div(Operator, LeftBinaryAssociation):
    symbols = [Literal("/").suppress()]
    @property
    def function(self) -> Callable[..., Base]:
        def f(
			x: Intable,
			y: Intable, 
		) -> Integer:
            if int(y) == 0:
                raise ZeroDivisionError()

            return Integer(
                operator.floordiv(int(x), int(y))
            )
        return f 

class GE(Operator, LeftBinaryAssociation):
    symbols = [Literal(">=").suppress()]

    @record(recorder, "{x} >= {y} -> {result} {r}")
    def evaluate(self, tid: int = -1):
        result = super().evaluate(tid)
        
        assert isinstance(result, Integer | IntegerList)
        self.outcome.update({
            "x": self.operands[0].outcome["result"],
            "y": self.operands[1].outcome["result"],
            "r": Integer(int(result))
        })

        return result
    
    @property
    def function(self):
        def f(
            x: IntegerList, 
            y: Union[Integer, IntegerList],
        ) -> IntegerList:
            if isinstance(x, Integer):
                x = IntegerList([x])
            return IntegerList([Integer(operator.ge(e, int(y))) for e in x])
        return f

class LE(Operator, LeftBinaryAssociation):
    symbols = [Literal("<=").suppress()]

    @record(recorder, "{x} <= {y} -> {result} {r}")
    def evaluate(self, tid: int = -1):
        result = super().evaluate(tid)
        
        assert isinstance(result, Integer | IntegerList)
        self.outcome.update({
            "x": self.operands[0].outcome["result"],
            "y": self.operands[1].outcome["result"],
            "r": Integer(int(result))
        })

        return result

    @property
    def function(self):
        def f(
            x: IntegerList, 
            y: Intable,
        ) -> IntegerList:
            if isinstance(x, Integer):
                x = IntegerList([x])
            return IntegerList([Integer(operator.le(e, int(y))) for e in x])
        return f

class GT(Operator, LeftBinaryAssociation):
    symbols = [Literal(">").suppress()]

    @record(recorder, "{x} > {y} -> {result} {r}")
    def evaluate(self, tid: int = -1):
        result = super().evaluate(tid)
        
        assert isinstance(result, Integer | IntegerList)
        self.outcome.update({
            "x": self.operands[0].outcome["result"],
            "y": self.operands[1].outcome["result"],
            "r": Integer(int(result))
        })

        return result

    @property
    def function(self):
        def f(
            x: IntegerList, 
            y: Intable,
        ) -> IntegerList:
            if isinstance(x, Integer):
                x = IntegerList([x])
            return IntegerList([Integer(operator.gt(e, int(y))) for e in x])
        return f

class LT(Operator, LeftBinaryAssociation):
    symbols = [Literal("<").suppress()]

    @record(recorder, "{x} < {y} -> {result} {r}")
    def evaluate(self, tid: int = -1):
        result = super().evaluate(tid)
        
        assert isinstance(result, Integer | IntegerList)
        self.outcome.update({
            "x": self.operands[0].outcome["result"],
            "y": self.operands[1].outcome["result"],
            "r": Integer(int(result))
        })

        return result

    @property
    def function(self):
        def f(
            x: IntegerList, 
            y: Intable,
        ) -> IntegerList:
            if isinstance(x, Integer):
                x = IntegerList([x])
            return IntegerList([Integer(operator.lt(e, int(y))) for e in x])
        return f

class EQ(Operator, LeftBinaryAssociation):
    symbols = [Literal("==").suppress()]

    @record(recorder, "{x} == {y} -> {result} {r}")
    def evaluate(self, tid: int = -1):
        result = super().evaluate(tid)
        
        assert isinstance(result, Integer | IntegerList)
        self.outcome.update({
            "x": self.operands[0].outcome["result"],
            "y": self.operands[1].outcome["result"],
            "r": Integer(int(result))
        })

        return result

    @property
    def function(self):
        def f(
            x: IntegerList, 
            y: Union[Integer, IntegerList],
        ) -> IntegerList:
            if isinstance(x, Integer):
                x = IntegerList([x])
            return IntegerList([Integer(operator.eq(e, int(y))) for e in x])
        return f

class NE(Operator, LeftBinaryAssociation):
    symbols = [Literal("!=").suppress()]

    @record(recorder, "{x} != {y} -> {result} {r}")
    def evaluate(self, tid: int = -1):
        result = super().evaluate(tid)
        
        assert isinstance(result, Integer | IntegerList)
        self.outcome.update({
            "x": self.operands[0].outcome["result"],
            "y": self.operands[1].outcome["result"],
            "r": Integer(int(result))
        })
        return result

    @property
    def function(self):
        def f(
            x: Intable, 
            y: Intable,
        ) -> IntegerList:
            if isinstance(x, Integer):
                x = IntegerList([x])
            return IntegerList([Integer(operator.ne(e, int(y))) for e in x])
        return f

class KeepMax(Operator, LeftBinaryAssociation):
    symbols = [
        Literal("K").suppress(),
        Literal("k").suppress(),
    ]

    @record(recorder, "{l}k{amount} -> {result}")
    def evaluate(self, tid: int = -1) -> Base:
        result = super().evaluate(tid)
        operand = self.operands[0].outcome["result"]

        assert isinstance(result, IntegerList)
        assert isinstance(operand, IntegerList)
        operan = [x for x in operand] 

        for x in result:
            if x in operan:  
                operan.remove(x) 

        removed = ", ".join(map(
            lambda x: "~~" + str(x) + "~~", operand
        ))
        accepted = ", ".join(map(
            str, result
        ))
        l = String(f"[{removed}, {accepted}]")
        self.outcome.update(
            {"l": l, "amount": self.operands[1].outcome["result"]}
        )


        return result

    @property
    def function(self) -> Callable[..., Base]:
        def f(
            l: IntegerList, 
            amount: Intable
        ) -> IntegerList:
            result = IntegerList(x for x in l) 
            while len(result) > int(amount):
                result.remove(min(result))
            return result
        return f

class KeepMin(Operator, LeftBinaryAssociation):
    symbols = [
        Literal("L").suppress(),
        Literal("l").suppress(),
    ]
    
    @record(recorder, "{l}l{amount} -> {result}")
    def evaluate(self, tid: int = -1) -> Base:
        result = super().evaluate(tid)

        operand = self.operands[0].outcome["result"]
        assert isinstance(result, IntegerList)
        assert isinstance(operand, IntegerList)
        operan = [x for x in operand] 
        for x in result:
            if x in operan:
                operan.remove(x) 

        removed = ", ".join(map(
            lambda x: "~~" + str(x) + "~~", operan
        ))
        accepted = ", ".join(map(
            str, result
        ))
        l = String(f"[{removed}, {accepted}]")
        self.outcome.update(
            {"l": l, "amount": self.operands[1].outcome["result"]}
        )

        return result

    @property
    def function(self) -> Callable[..., Base]:
        def f(
            l: IntegerList, 
            amount: Intable
        ) -> IntegerList:
            result = IntegerList(x for x in l)
            while len(result) > int(amount):
                result.remove(max(result)) 
            return result
        return f 

