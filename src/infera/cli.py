
import argparse
from collections.abc import Sequence
from os import wait

from infera.rewrite import Rule, rewrite
from infera.tabulate import is_tautology
from infera.lang import Expr, Term, TheoremDef, parse_stmt
from infera import sexp

def prove(expr: Expr, rules: list[Rule]) -> bool:
    match expr:
        case Term(operator='implies'):
            premise = expr.children[0]
            goal = expr.children[1]
            return rewrite(premise, goal, rules)
        case Term(operator='and'):
            for child in expr.children:
                if not prove(child, rules):
                    return False
            return True
        case Term(operator='equiv'):
            # FIXME solve using equivalence substitutions
            # FIXME might be better to rewrite to (a => b) ^ (b => a) and then solve
            left = expr.children[0]
            right = expr.children[1]
            return rewrite(left, right, rules) and rewrite(right, left, rules)
        case _:
            raise RuntimeError(f"do not yet know how to prove {expr}")

def extend(rules: list[Rule], expr: Expr, name: str) -> None:
    match expr:
        case Term(operator='implies'):
            premise = expr.children[0]
            goal = expr.children[1]
            rules.append(Rule(premise, goal, name))
        case Term(operator='equiv'):
            left = expr.children[0]
            right = expr.children[1]
            rules.append(Rule(left, right, name))
            rules.append(Rule(right, left, name))
        case Term(operator='and'):
            for i, child in enumerate(expr.children):
                extend(rules, child, f'{name}_{i}')
        case _:
            raise RuntimeError(f"did not yet know how to add proven {expr} to the KB")

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs=1, help='The file to verfiy')
    args = parser.parse_args(argv)
    fname = args.file[0]

    with open(fname, 'r') as f:
        text = f.read()
    els = sexp.parse_file(text, filename=fname)

    rules = []
    for el in els:
        stmt = parse_stmt(el)
        if isinstance(stmt, TheoremDef):

            if stmt.tactic == 'tabulate':
                proven = is_tautology(stmt.expr)
            elif stmt.tactic == 'rewrite':
                proven = prove(stmt.expr, rules)
            else:
                raise RuntimeError(f"unknown tactic '{stmt.tactic}'")

            if proven:
                extend(rules, stmt.expr, stmt.name)
                print(f'✅️ {stmt.name or stmt.expr}')
            else:
                print(f'❌️ {stmt.name or stmt.expr}')

    return 0
