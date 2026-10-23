
import ast
import math
import operator
import re
from qgis.core import (QgsExpression,QgsExpressionContext,QgsExpressionContextScope)

BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}

UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

ALLOWED_FUNCTIONS = {
    "min": min,
    "max": max,
}

CONSTANT_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class FormulaError(ValueError):
    """Raised when a formula is invalid or cannot be evaluated."""


def validate_constant_name(name):
    if not isinstance(name, str) or not CONSTANT_NAME_PATTERN.fullmatch(name):
        raise FormulaError(f"Invalid constant name: {name!r}")

    if name in ALLOWED_FUNCTIONS:
        raise FormulaError(f"Reserved name: {name}")


def check_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FormulaError("The formula must produce a number.")
    if not math.isfinite(value):
        raise FormulaError("The formula produced a non-finite result.")
    return value