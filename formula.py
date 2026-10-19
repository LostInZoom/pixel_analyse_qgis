
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


# def evaluate_formula(expression, variables, constants=None):
#     """Evaluate a restricted mathematical expression."""

#     if not isinstance(expression, str) or not expression.strip():
#         raise FormulaError("The formula is empty.")

#     constants = constants or {}

#     if not isinstance(constants, dict):
#         raise FormulaError("Constants must be a dictionary.")

#     for name in constants:
#         validate_constant_name(name)

#     allowed_values = {}

#     for name, value in variables.items():
#         if not isinstance(name, str):
#             raise FormulaError("Invalid variable name.")

#         allowed_values[name] = value

#     for name, value in constants.items():
#         if name in allowed_values:
#             raise FormulaError(f"Constant conflicts with variable: {name}")

#         if name in ALLOWED_FUNCTIONS:
#             raise FormulaError(f"Reserved name: {name}")

#         allowed_values[name] = value

#     expression = expression.replace("^", "**")

#     try:
#         tree = ast.parse(expression, mode="eval")
#     except (SyntaxError, ValueError) as error:
#         raise FormulaError("Invalid formula syntax.") from error

#     def evaluate(node):
#         if isinstance(node, ast.Expression):
#             return evaluate(node.body)

#         if isinstance(node, ast.Constant):
#             if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
#                 raise FormulaError("Only numeric constants are allowed.")

#             return node.value

#         if isinstance(node, ast.Name):
#             if node.id not in allowed_values:
#                 raise FormulaError(f"Unknown variable or constant: {node.id}")

#             return allowed_values[node.id]

#         if isinstance(node, ast.BinOp):
#             operation = BINARY_OPERATORS.get(type(node.op))

#             if operation is None:
#                 raise FormulaError("This operator is not allowed.")

#             left = evaluate(node.left)
#             right = evaluate(node.right)

#             if isinstance(node.op, ast.Pow):
#                 if abs(right) > 20:
#                     raise FormulaError("The absolute value of an exponent cannot exceed 20.")

#             try:
#                 result = operation(left, right)
#             except (ArithmeticError, OverflowError, ValueError) as error:
#                 raise FormulaError("The operation could not be evaluated.") from error

#             return check_number(result)

#         if isinstance(node, ast.UnaryOp):
#             operation = UNARY_OPERATORS.get(type(node.op))

#             if operation is None:
#                 raise FormulaError("This unary operator is not allowed.")

#             return check_number(operation(evaluate(node.operand)))

#         if isinstance(node, ast.Call):
#             if not isinstance(node.func, ast.Name):
#                 raise FormulaError("Only min() and max() are allowed.")

#             function = ALLOWED_FUNCTIONS.get(node.func.id)

#             if function is None:
#                 raise FormulaError(f"Function not allowed: {node.func.id}")

#             if node.keywords:
#                 raise FormulaError("Named function arguments are not allowed.")

#             if len(node.args) < 2:
#                 raise FormulaError(
#                     "min() and max() require at least two arguments."
#                 )

#             arguments = [evaluate(argument) for argument in node.args]

#             return check_number(function(*arguments))

#         raise FormulaError(
#             "This element is not allowed in a formula."
#         )
#     return check_number(evaluate(tree))

# def evaluate_output_expression(expression_text, variables, constants=None):
#     expression = QgsExpression(expression_text)

#     context = QgsExpressionContext()
#     scope = QgsExpressionContextScope("Pixel Energy")

#     for name, value in variables.items():
#         scope.setVariable(name, value)

#     for name, value in (constants or {}).items():
#         scope.setVariable(name, value)

#     context.appendScope(scope)

#     if not expression.prepare(context):
#         raise ValueError(f"Invalid output formula: {expression.parserErrorString()}")
#     result = expression.evaluate(context)

#     if expression.hasEvalError():
#         raise ValueError(f"Output formula evaluation error: {expression.evalErrorString()}")

#     if result is None:
#         raise ValueError("Output formula returned no result.")

#     try:
#         return float(result)
#     except (TypeError, ValueError):
#         raise ValueError(f"Output formula did not return a number: {result}")

def check_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FormulaError("The formula must produce a number.")
    if not math.isfinite(value):
        raise FormulaError("The formula produced a non-finite result.")
    return value