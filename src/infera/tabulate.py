#!/usr/bin/env python3

from collections.abc import Generator
from itertools import permutations
from dataclasses import dataclass

type Expr = Var | Not | And | Or | Implies | Equiv

Env = dict[str, bool]

class ExprBase:
    pass

@dataclass
class Var(ExprBase):
    name: str

@dataclass
class Not(ExprBase):
    child: Expr

@dataclass
class And(ExprBase):
    left: Expr
    right: Expr

@dataclass
class Or(ExprBase):
    left: Expr
    right: Expr

@dataclass
class Equiv(ExprBase):
    left: Expr
    right: Expr

@dataclass
class Implies(ExprBase):
    premise: Expr
    consequent: Expr

def implies(precedent: bool, consequent: bool) -> bool:
    """
    Python has no built-in function for calculating the logical implication so we do the next best thing.
    """
    return not precedent or consequent

def variables(expr: Expr) -> Generator[str, None, None]:
    match expr:
        case Var(name): yield name
        case Not(child): yield from variables(child)
        case And(left, right):
            yield from variables(left)
            yield from variables(right)
        case Or(left, right):
            yield from variables(left)
            yield from variables(right)
        case Equiv(left, right):
            yield from variables(left)
            yield from variables(right)
        case Implies(premise, cons):
            yield from variables(premise)
            yield from variables(cons)

def eval(expr: Expr, env: Env) -> bool:
    match expr:
        case Var(name): return env[name]
        case Not(child): return eval(child, env)
        case And(left, right): return eval(left, env) and eval(right, env)
        case Or(left, right): return eval(left, env) or eval(right, env)
        case Equiv(left, right): return eval(left, env) == eval(right, env)
        case Implies(premise, consequent): return implies(eval(premise, env), eval(consequent, env))

def encode(value: bool) -> str:
    return '1' if value else '0'

def is_tautology(expr: Expr) -> bool:

    vs = list(sorted(set(variables(expr))))

    env = {}
    for v in vs:
        env[v] = False

    is_taut = True
    n = len(vs)

    out = ''
    for i, v in enumerate(vs):
        if i > 0: out += ' '
        out += v
    out += ' | ' + to_string(expr)
    print(out)

    for i in range(2**n):

        for k, v in enumerate(vs):
            env[v] = (i // ((2**n) // (2**(k+1)) )) % 2 == 1

        truthy = eval(expr, env)

        out = ''
        for j, v in enumerate(vs):
            if j > 0:
                out += ' '
            out += encode(env[v])
        out += ' | ' + encode(truthy)
        print(out)

        if not truthy:
            is_taut = False

    if is_taut:
        print('Statement is a tautology!')
    else:
        print('Statement is NOT a tautology!')

    return is_taut

def to_string(expr: Expr) -> str:
    match expr:
        case Var(name): return name
        case Not(child): return '¬' + to_string(child)
        case Implies(left, right): return to_string(left) + ' ⇒ ' + to_string(right)
        case And(left, right): return to_string(left) + ' ^ ' + to_string(right)
        case Or(left, right): return to_string(left) + ' ∨ ' + to_string(right)
        case Equiv(left, right): return to_string(left) + ' ⟺  ' + to_string(right)

if __name__ == "__main__":
    expr = Equiv(
        Or(
            Implies(Var("A"), Var("C")),
            Implies(Var("B"), Var("C")),
        ),
        Implies(
            And(Var("A"), Var("B")),
            Var("C")
        )
    )
    is_tautology(expr)

    expr = Equiv(
        And(
            Implies(Var("C"), Var("A")),
            Implies(Var("C"), Var("B")),
        ),
        Implies(
            Var("C"),
            And(Var("A"), Var("B")),
        )
    )
    is_tautology(expr)

