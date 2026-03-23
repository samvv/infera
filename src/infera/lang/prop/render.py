
from collections.abc import Sequence

from .node import PropTerm, PropVar, Prop


def render_prop(expr: Prop) -> str:
    """
    Render the given proposition to pseudo-mathematical notation.
    """

    def is_wide(prop: Prop) -> bool:
        match prop:
            case PropVar():
                return False
            case PropTerm() if len(prop.children) == 1:
                return is_wide(prop.children[0])
            case PropTerm():
                return True

    def binary(symbol: str, children: Sequence[Prop]) -> str:
        left = children[0]
        right = children[1]
        str_left = f'({left})' if is_wide(left) else f'{left}'
        str_right = f'({right})' if is_wide(right) else f'{right}'
        return f'{str_left} {symbol} {str_right}'

    def unary(symbol: str, children: Sequence[Prop]) -> str:
        child = children[0]
        inner = f'({child})' if is_wide(child) else f'{child}'
        return f'{symbol} {inner}'

    match expr:
        case PropVar(name):
            return name
        case PropTerm(operator='not'):
            return unary('¬', expr.children)
        case PropTerm(operator='and'):
            return binary('∧', expr.children)
        case PropTerm(operator='or'):
            return binary('∨', expr.children)
        case PropTerm(operator='equiv'):
            return binary('⇔', expr.children)
        case PropTerm(operator='implies'):
            return binary('⇒', expr.children)
        case _:
            raise RuntimeError(f"could not convert expression to mathematical notation")


