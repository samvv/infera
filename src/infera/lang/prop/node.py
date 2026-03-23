

from dataclasses import dataclass
from typing import Any, TypeGuard
from frozenlist import FrozenList

from infera.abstract import AbstractNode
from infera.sexp import List, SExp, Sym


class PropBase(AbstractNode):
    pass


@dataclass(frozen=True)
class PropVar(PropBase):
    """
    A single variable in propositional logic.

    E.g. the `a` in `a v (b => c)`
    """
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class PropTerm(PropBase):
    """
    A connective with one or more children.

    E.g. `not a` or `a v b` where `a` and `b` are children.
    """
    operator: str
    children: FrozenList[Prop]


    @property
    def arity(self) -> int:
        return len(self.children)

    def __str__(self) -> str:
        out = '('
        out += self.operator
        for child in self.children:
            out += ' ' + str(child)
        out += ')'
        return out


type Prop = PropVar | PropTerm


def is_prop(value: Any) -> TypeGuard[Prop]:
    return isinstance(value, PropVar) or isinstance(value, PropTerm)


@dataclass(frozen=True)
class TermChildIndex:
    """
    An edge to a child of a Term.
    """
    offset: int

    def get(self, expr: Prop) -> Prop:
        assert(isinstance(expr, PropTerm))
        return expr.children[self.offset]

    def set(self, expr: Prop, new_expr: Prop) -> Prop:
        assert(isinstance(expr, PropTerm))
        new_children = list(expr.children)
        new_children[self.offset] = new_expr
        new_children = FrozenList(new_children)
        new_children.freeze()
        return PropTerm(expr.operator, new_children)

    def __str__(self) -> str:
        return f'.{self.offset}'


type Index = TermChildIndex


def parse_expr(sexp: SExp) -> Prop:
    if isinstance(sexp, Sym):
        return PropVar(sexp.name)
    if isinstance(sexp, List):
        assert(len(sexp.head) > 0)
        assert(sexp.tail is None)
        name = sexp.head[0]
        assert(isinstance(name, Sym))
        # TODO check arity of `name.name`
        args = FrozenList(parse_expr(arg) for arg in sexp.head[1:])
        args.freeze()
        return PropTerm(name.name, args)
    raise RuntimeError(f"could not parse S-expression {sexp} into first-order logic expression")



