#!/usr/bin/env python3

import math
from collections.abc import Generator
from dataclasses import dataclass
from typing import Sequence, assert_never
from copy import copy

from infera.sexp import SExp, Sym, List

class Table:

    def __init__(self, output: list[bool]) -> None:
        self.output = output

    @staticmethod
    def for_n_vars(n: int) -> 'Table':
        return Table([ False for _ in range(2 ** n) ])

    def index(self, values: Sequence[bool]) -> int:
        k = 0
        for i, b in enumerate(values):
            if b:
                k += 2 ** i;
        return k

    def set(self, values: Sequence[bool], truthy: bool) -> None:
        k = self.index(values)
        self.output[k] = truthy;

    def get(self, values: Sequence[bool]) -> bool:
        return self.output[self.index(values)]

    def var_count(self) -> int:
        return math.ceil(math.log2(float(len(self.output))))

NOT_TABLE = Table.for_n_vars(1)
NOT_TABLE.set([False], True)
NOT_TABLE.set([True], False)

AND_TABLE = Table.for_n_vars(2)
AND_TABLE.set([False, False], False)
AND_TABLE.set([False, True], False)
AND_TABLE.set([True, False], False)
AND_TABLE.set([True, True], True)

OR_TABLE = Table.for_n_vars(2)
OR_TABLE.set([False, False], False)
OR_TABLE.set([False, True], True)
OR_TABLE.set([True, False], True)
OR_TABLE.set([True, True], True)

IMPLIES_TABLE = Table.for_n_vars(2)
IMPLIES_TABLE.set([False, False], True)
IMPLIES_TABLE.set([False, True], True)
IMPLIES_TABLE.set([True, False], False)
IMPLIES_TABLE.set([True, True], True)

EQUIV_TABLE = Table.for_n_vars(2)
EQUIV_TABLE.set([False, False], True)
EQUIV_TABLE.set([False, True], False)
EQUIV_TABLE.set([True, False], False)
EQUIV_TABLE.set([True, True], True)

XOR_TABLE = Table.for_n_vars(2)
XOR_TABLE.set([False, False], False)
XOR_TABLE.set([False, True], True)
XOR_TABLE.set([True, False], True)
XOR_TABLE.set([True, True], False)

@dataclass
class Operator:
    name: str
    alt_name: str
    table: Table

operators = [
    Operator('and', '∧',  AND_TABLE),
    Operator('or', '∨', OR_TABLE),
    Operator('implies', '⇒', IMPLIES_TABLE),
    Operator('xor', '⊻', XOR_TABLE),
    Operator('equiv', '⇔', EQUIV_TABLE),
    Operator('not', '¬', NOT_TABLE),
]

DEFAULT_ENV = {}
for operator in operators:
    DEFAULT_ENV[operator.name] = operator

Env = dict[str, bool]

type Expr = Var | Term

class ExprBase:
    pass

@dataclass
class Var(ExprBase):
    name: str

    def __str__(self) -> str:
        return self.name

@dataclass
class Term(ExprBase):
    operator: str
    children: Sequence[Expr]

    def __str__(self) -> str:
        out = '('
        out += self.operator
        for child in self.children:
            out += ' ' + str(child)
        out += ')'
        return out

def variables(expr: Expr) -> Generator[str, None, None]:
    match expr:
        case Var(name): yield name
        case Term():
            for child in expr.children:
                yield from variables(child)
        case _:
            assert_never(expr)

def eval(expr: Expr, env: Env) -> bool:
    match expr:
        case Var(name): return env[name]
        case Term():
            values = [ eval(child, env) for child in expr.children ]
            operator = env[expr.operator]
            assert(isinstance(operator, Operator))
            return operator.table.get(values)
        case _:
            assert_never(expr)

def encode_truth_value(value: bool) -> str:
    return '1' if value else '0'

def is_tautology(expr: Expr) -> bool:

    vs = list(sorted(set(variables(expr))))

    env = copy(DEFAULT_ENV)
    for v in vs:
        env[v] = False

    is_taut = True
    n = len(vs)

    out = ''
    for i, v in enumerate(vs):
        if i > 0: out += ' '
        out += v
    out += f' | {expr}'
    print(out)

    for i in range(2**n):

        for k, v in enumerate(vs):
            env[v] = (i // ((2**n) // (2**(k+1)) )) % 2 == 1

        truthy = eval(expr, env)

        out = ''
        for j, v in enumerate(vs):
            if j > 0:
                out += ' '
            out += encode_truth_value(env[v])
        out += ' | ' + encode_truth_value(truthy)
        print(out)

        if not truthy:
            is_taut = False

    return is_taut

def parse_expr(sexp: SExp) -> Expr:
    if isinstance(sexp, Sym):
        return Var(sexp.name)
    if isinstance(sexp, List):
        assert(len(sexp.head) > 0)
        assert(sexp.tail is None)
        name = sexp.head[0]
        assert(isinstance(name, Sym))
        # TODO check arity of `name.name`
        args = list(parse_expr(arg) for arg in sexp.head[1:])
        return Term(name.name, args)
    raise RuntimeError("could not parse S-expression into first-order logic expression")

if __name__ == "__main__":
    from infera import sexp
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs=1)
    args = parser.parse_args()
    fname = args.file[0]

    with open(fname, 'r') as f:
        text = f.read()
    prog = sexp.parse_file(text)
    for element in prog:
        expr = parse_expr(element)
        if is_tautology(expr):
            print('Statement is a tautology!')
        else:
            print('Statement is NOT a tautology!')
