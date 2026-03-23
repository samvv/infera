
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, TypeIs

from infera.lang import pred
from infera.lang import prop
from infera.sexp import Keyword, List, SExp, Sym

type TacticName = Literal['tabulate', 'rewrite']

@dataclass
class TheoremDef:
    name: str
    expr: prop.Prop | pred.Formula
    tactic: TacticName

type Stmt = TheoremDef

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

def is_tactic_name(name: str) -> TypeIs[TacticName]:
    return name in [ 'rewrite', 'tabulate' ]

def parse_stmt(sexp: SExp) -> Stmt:
    assert(isinstance(sexp, List))
    assert(len(sexp.head) > 0)
    assert(sexp.tail is None)
    assert(isinstance(sexp.head[0], Sym))
    kw = sexp.head[0].name
    if kw == 'defthm':
        assert(isinstance(sexp.head[1], Sym))
        name = sexp.head[1].name
        expr = prop.parse_expr(sexp.head[2])
        kws = parse_keywords(sexp.head[3:])
        val_tactic = kws.get('tactic', Sym('rewrite'))
        assert(isinstance(val_tactic, Sym) and is_tactic_name(val_tactic.name))
        return TheoremDef(name, expr, val_tactic.name)
    raise RuntimeError(f"unexpected keyword '{kw}'")

