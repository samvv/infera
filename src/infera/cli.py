
import argparse
from collections.abc import Sequence

from infera.lang.prop import PropKB, prove_by_rewriting, prove_by_tabulation
from infera.lang import TheoremDef, parse_stmt
from infera import sexp
from infera.util import Progress

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
    kb = PropKB()
    for el in els:
        stmt = parse_stmt(el)
        if isinstance(stmt, TheoremDef):

            proven = None
            if stmt.tactic == 'tabulate':
                proven = prove_by_tabulation(stmt.expr, kb, progress)
            elif stmt.tactic == 'rewrite':
                proven = prove_by_rewriting(stmt.expr, kb, progress)
            else:
                raise RuntimeError(f"unknown tactic '{stmt.tactic}'")

            if proven is None:
                wrong += 1
                print(f'❌️ {stmt.name or stmt.expr}', file=progress)
            else:
                kb.add(stmt.expr, stmt.name)
                right += 1
                print(f'✅️ {stmt.name or stmt.expr}', file=progress)

    progress.finish(f"All theorems inspected. {wrong} pending and {right} proven.")
    return 0
