
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal
from frozenlist import FrozenList

from infera.sexp import Keyword, List, SExp, Sym

type Expr = Var | Term

class ExprBase:
    pass

@dataclass(frozen=True)
class Var(ExprBase):
    name: str

    def __str__(self) -> str:
        return self.name

@dataclass(frozen=True)
class Term(ExprBase):
    operator: str
    children: FrozenList[Expr]

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


def is_wide(expr: Expr) -> bool:
    return not (isinstance(expr, Var) or expr.arity <= 1)


def render(expr: Expr) -> str:

    def binary(symbol: str, children: Sequence[Expr]) -> str:
        left = children[0]
        right = children[1]
        str_left = f'({left})' if is_wide(left) else f'{left}'
        str_right = f'({right})' if is_wide(right) else f'{right}'
        return f'{str_left} {symbol} {str_right}'

    def unary(symbol: str, children: Sequence[Expr]) -> str:
        child = children[0]
        inner = f'({child})' if is_wide(child) else f'{child}'
        return f'{symbol} {inner}'

    match expr:
        case Var(name):
            return name
        case Term(operator='not'):
            return unary('¬', expr.children)
        case Term(operator='and'):
            return binary('∧', expr.children)
        case Term(operator='or'):
            return binary('∨', expr.children)
        case Term(operator='equiv'):
            return binary('⇔', expr.children)
        case Term(operator='implies'):
            return binary('⇒', expr.children)
        case _:
            raise RuntimeError(f"could not convert expression to mathematical notation")

type TacticName = Literal['tabulate', 'rewrite']

@dataclass
class TheoremDef:
    name: str
    expr: Expr
    tactic: TacticName

type Stmt = TheoremDef

def parse_expr(sexp: SExp) -> Expr:
    if isinstance(sexp, Sym):
        return Var(sexp.name)
    if isinstance(sexp, List):
        assert(len(sexp.head) > 0)
        assert(sexp.tail is None)
        name = sexp.head[0]
        assert(isinstance(name, Sym))
        # TODO check arity of `name.name`
        args = FrozenList(parse_expr(arg) for arg in sexp.head[1:])
        args.freeze()
        return Term(name.name, args)
    raise RuntimeError(f"could not parse S-expression {sexp} into first-order logic expression")

def parse_keywords(l: Sequence[SExp]) -> dict[str, SExp]:
    out = {}
    i = 0
    while i < len(l):
        kw = l[i]
        assert(isinstance(kw, Keyword))
        i += 1
        if i == len(l):
            raise RuntimeError(f"keyword argument #:{kw.name} missing a value")
        value = l[i]
        i += 1
        out[kw.name] = value
    return out

def parse_stmt(sexp: SExp) -> Stmt:
    assert(isinstance(sexp, List))
    assert(len(sexp.head) > 0)
    assert(sexp.tail is None)
    assert(isinstance(sexp.head[0], Sym))
    kw = sexp.head[0].name
    if kw == 'defthm':
        assert(isinstance(sexp.head[1], Sym))
        name = sexp.head[1].name
        expr = parse_expr(sexp.head[2])
        kws = parse_keywords(sexp.head[3:])
        val_tactic = kws.get('tactic', Sym('rewrite'))
        assert(isinstance(val_tactic, Sym))
        return TheoremDef(name, expr, val_tactic.name)
    raise RuntimeError(f"unexpected keyword '{kw}'")

