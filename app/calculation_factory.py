"""
Calculation factory to compute results based on operation type.
"""
from typing import Callable
from app.operations import add, subtract, multiply, divide


class CalculationFactory:
    """Small factory to map operation string to function and compute result."""

    _map: dict[str, Callable[[float, float], float]] = {
        "add": add,
        "subtract": subtract,
        "multiply": multiply,
        "divide": divide,
    }

    @classmethod
    def compute(cls, operation: str, a: float, b: float) -> float:
        op = operation.lower()
        if op not in cls._map:
            raise ValueError(f"Unsupported operation: {operation}")
        return cls._map[op](a, b)
