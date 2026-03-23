
import argparse
from collections.abc import Sequence

from infera.lang.prop.rewrite import Rule, rewrite
from infera.lang.prop.tabulate import is_tautology
from infera.lang.prop import Prop, PTerm
from infera.lang import TheoremDef, parse_stmt
from infera import sexp
from infera.util import Progress

def prove(expr: Prop, rules: list[Rule], progress: Progress) -> bool:
    match expr:
        case PTerm(operator='implies'):
            premise = expr.children[0]
            goal = expr.children[1]
            return rewrite(premise, goal, rules, progress)
        case PTerm(operator='and'):
            for child in expr.children:
                if not prove(child, rules, progress):
                    return False
            return True
        case PTerm(operator='equiv'):
            # FIXME solve using equivalence substitutions
            # FIXME might be better to rewrite to (a => b) ^ (b => a) and then solve
            left = expr.children[0]
            right = expr.children[1]
            return rewrite(left, right, rules, progress) and rewrite(right, left, rules, progress)
        case _:
            raise RuntimeError(f"do not yet know how to prove {expr}")

def extend(rules: list[Rule], expr: Prop, name: str) -> None:
    match expr:
        case PTerm(operator='implies'):
            premise = expr.children[0]
            goal = expr.children[1]
            rules.append(Rule(premise, goal, name))
        case PTerm(operator='equiv'):
            left = expr.children[0]
            right = expr.children[1]
            rules.append(Rule(left, right, name))
            rules.append(Rule(right, left, name))
        case PTerm(operator='and'):
            for i, child in enumerate(expr.children):
                extend(rules, child, f'{name}_{i}')
        case _:
            raise RuntimeError(f"did not yet know how to add proven {expr} to the KB")

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs=1, help='The file to verfiy')
    args = parser.parse_args(argv)
    fname = args.file[0]
    progress = Progress()

    with open(fname, 'r') as f:
        text = f.read()
    els = sexp.parse_file(text, filename=fname)

    wrong = 0
    right = 0
    rules = []
    for el in els:
        stmt = parse_stmt(el)
        if isinstance(stmt, TheoremDef):

            if stmt.tactic == 'tabulate':
                proven = is_tautology(stmt.expr)
            elif stmt.tactic == 'rewrite':
                proven = prove(stmt.expr, rules, progress)
            else:
                raise RuntimeError(f"unknown tactic '{stmt.tactic}'")

            if proven:
                extend(rules, stmt.expr, stmt.name)
                right += 1
                print(f'✅️ {stmt.name or stmt.expr}', file=progress)
            else:
                wrong += 1
                print(f'❌️ {stmt.name or stmt.expr}', file=progress)

    progress.finish(f"All theorems inspected. {wrong} pending and {right} proven.")
    return 0
