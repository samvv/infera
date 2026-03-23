
from typing import assert_never
from .node import Connected, Function, Node, Predicate, Quantized, Var


def is_wide(node: Node) -> bool:
    """
    Does this node consume any spaces when parsed or emitted?
    """
    match node:
        case Var():
            return False
        case Function():
            return False
        case Predicate():
            return False
        case Quantized():
            return True
        case Connected():
            return node.arity > 1
        case _:
            assert_never(node)

