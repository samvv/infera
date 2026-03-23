
from typing import assert_never
from .node import PredConnective, PredFunction, Node, PredPredicate, PredQuantized, PredVar


def is_wide(node: Node) -> bool:
    """
    Does this node consume any spaces when parsed or emitted?
    """
    match node:
        case PredVar():
            return False
        case PredFunction():
            return False
        case PredPredicate():
            return False
        case PredQuantized():
            return True
        case PredConnective():
            return node.arity > 1
        case _:
            assert_never(node)

