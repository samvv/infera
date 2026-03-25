#!/usr/bin/env python3

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from frozenlist import FrozenList
from typing import assert_never, override
import heapq

from infera.search import ConstantHeuristic, Heuristic, WeightedHeuristic
from infera.util import Progress, frozen
from ..kb import PropKB, Rule
from ..node import Index, Prop, PropTerm, PropVar, TermChildIndex, prop_size


type Path = FrozenList[Index]


def resolve(prop: Prop, path: Path) -> Prop:
    for index in path:
        prop = index.get(prop)
    return prop


def assign(root: Prop, path: Path, replace: Prop) -> Prop:
    def visit(prop: Prop, i: int) -> Prop:
        if i == len(path):
            return replace
        index = path[i]
        child = index.get(prop)
        return index.set(prop, visit(child, i+1))
    return visit(root, 0)


VarSub = dict[str, Prop]


class UnifyError(RuntimeError):
    pass


def unify(left: Prop, right: Prop) -> VarSub:
    out = VarSub()
    if isinstance(left, PropVar):
        out[left.name] = right
    elif isinstance(right, PropVar):
        out[right.name] = left
    elif isinstance(left, PropTerm) and isinstance(right, PropTerm) and left.operator == right.operator:
        for a, b in zip(left.children, right.children):
            out.update(unify(a, b))
    else:
        raise UnifyError()
    return out


def equal(a: Prop, b: Prop) -> bool:
    if isinstance(a, PropVar) and isinstance(b, PropVar):
        return a.name == b.name
    if isinstance(a, PropTerm) and isinstance(b, PropTerm) and a.operator == b.operator:
        for l, r in zip(a.children, b.children):
            if not equal(l, r):
                return False
        return True
    return False


def substitute(expr: Prop, sub: VarSub) -> Prop:
    if isinstance(expr, PropVar):
        return sub.get(expr.name, expr)
    if isinstance(expr, PropTerm):
        changed = False
        new_children = []
        for child in expr.children:
            new_child = substitute(child, sub)
            if child is not new_child:
                changed = True
            new_children.append(new_child)
        new_children = FrozenList(new_children)
        new_children.freeze()
        return PropTerm(expr.operator, new_children) if changed else expr
    assert_never(expr)


def apply_rule(prop: Prop, rule: Rule) -> Prop | None:
    try:
        sub = unify(rule.pattern, prop)
    except UnifyError:
        return None
    return substitute(rule.result, sub)


def match_all(prop: Prop, kb: PropKB) -> Iterator[tuple[Rule, Prop]]:
    for rule in kb.match_rules(prop):
        result = apply_rule(prop, rule)
        if result is not None:
            yield rule, result


def search_one(premise: Prop, goal: Prop, kb: PropKB) -> Rule | None:
    for rule, result in match_all(premise, kb):
        try:
            unify(result, goal)
        except UnifyError:
            continue
        return rule


@dataclass
class Node:
    expr: Prop
    rule: tuple[Rule, Path] | None
    focus: Path
    parent: 'Node | None'


@dataclass(order=True)
class Weighted[T]:
    weight: float
    data: T = field(compare=False)


_empty_frozenlist = FrozenList()
_empty_frozenlist.freeze()


def enumerate_paths(prop: Prop, path: Path | None = None) -> Iterable[Path]:
    """
    This method MUST also include the empty path.
    """
    if path is None:
        path = frozen([])
    yield path
    if isinstance(prop, PropVar):
        return
    if isinstance(prop, PropTerm):
        for i, child in enumerate(prop.children):
            child_path = frozen([ *path, TermChildIndex(i) ])
            yield from enumerate_paths(child, child_path)
        return
    assert_never(prop)


class PropSizeHeuristic(Heuristic[Node]):

    @override
    def rate(self, curr: Node, goal: Node) -> float:
        return prop_size(curr.expr)


class MaxStepsExceededError(RuntimeError):

    def __init__(self, limit: int) -> None:
        super().__init__(f"limit of {limit} iterations reached")


type Step = tuple[Prop, Rule, Path]


def expand(node: Node, kb: PropKB) -> Iterable[Node]:
    redex = resolve(node.expr, node.focus)
    for rule in kb.match_rules(redex):
        new_redex = apply_rule(redex, rule)
        if new_redex is not None:
            new_prop = assign(node.expr, node.focus, new_redex)
            for path in enumerate_paths(new_redex):
                full_path = frozen([ *node.focus, *path ])
                yield Node(new_prop, (rule, node.focus), full_path, node)


def search(
    premise: Prop,
    goal: Prop,
    kb: PropKB,
    h: Heuristic | None = None,
    progress: Progress | None = None,
    limit: int = 0
) -> tuple[list[Step] | None, int]:

    if h is None:
        h = ConstantHeuristic(1.0)

    count = 0
    queue = list[Weighted[Node]]()
    # queue.append(Weighted(0, Node(premise, None, _empty_frozenlist, None)))

    def enqueue(node: Node) -> None:
        #print(f'++++++ {highlight(node.expr, node.path)} @ {node.rule} ~ {h.rate(node, goal)}', file=progress)
        heapq.heappush(queue, Weighted(h.rate(node, goal), node))

    def dump(node: Node) -> None:
        if node.rule is not None:
            rule, path = node.rule
            print(f'{highlight(node.expr, path)} @ {rule} ~ {h.rate(node, goal)}', file=progress)
        else:
            print(f'{node.expr} ~ {h.rate(node, goal)}', file=progress)

    # Register all possible rewrite points for the premise
    for path in enumerate_paths(premise):
        enqueue(Node(premise, None, path, None))

    node = None
    visited = set[tuple[Prop, Path]]()
    while queue:
        # for node in queue:
        #     print(f">>>> {highlight(node.data.expr, node.data.path)} ~ {node.weight}")
        node = heapq.heappop(queue).data
        if progress is not None:
            progress.status(f"Search iteration {count}")
        if limit > 0 and limit == count:
            raise MaxStepsExceededError(limit=limit)
        count += 1
        node_key = (node.expr, node.focus)
        if node_key in visited:
            continue
        visited.add(node_key)
        if equal(node.expr, goal):
            break
        dump(node)
        for new_node in expand(node, kb):
            enqueue(new_node)

    if node is None:
        return None, count
    out = []
    while node.parent is not None:
        r, p = nonnull(node.rule)
        out.append((node.expr, r, p))
        node = node.parent
    out.reverse()
    return out, count


def nonnull[T](value: T | None) -> T:
    assert(value is not None)
    return value


SUB_START = '\033[1m\033[92m'
SUB_END   = '\033[0m'


def highlight(prop: Prop, path: Path | None) -> str:
    out = ''
    if path is not None and not path:
        out += SUB_START
    if isinstance(prop, PropTerm):
        out += '(' + prop.operator
        for i, child in enumerate(prop.children):
            out += ' ' + highlight(child, path[1:] if path and path[0] == TermChildIndex(i) else None)
        out += ')'
    elif isinstance(prop, PropVar):
        out += str(prop)
    else:
        assert_never(prop)
    if path is not None and not path:
        out += SUB_END
    return out


def rewrite_to_goal(
    premise: Prop,
    goal: Prop,
    kb: PropKB,
    progress: Progress
) -> bool:
    print(f"Premise: {premise}", file=progress)
    print(f"Goal: {goal}", file=progress)
    solution, count = search(
        premise,
        goal,
        kb,
        progress=progress,
        h=WeightedHeuristic([ (1.0, PropSizeHeuristic()) ]),
        limit=8000
    )
    print(f"Searched {count} states", file=progress)
    if solution is None:
        print("Formula could not be solved.", file=progress)
        return False
    print("Steps:", file=progress)
    last = premise
    for i, (prop, rule, path) in enumerate(solution):
        print(f"{i+1}. {highlight(last, path)} ⇒ {prop} by rule {SUB_START}{rule.pattern}{SUB_END} ⊢ {rule.result}", file=progress)
        last = prop
    return True


def prove_by_rewriting(expr: Prop, kb: PropKB, progress: Progress) -> bool:
    # TODO we can probably just call rewrite_to_goal directly
    #      and consider the cases below optimisations
    match expr:
        case PropTerm(operator='implies'):
            premise = expr.children[0]
            goal = expr.children[1]
            return rewrite_to_goal(premise, goal, kb, progress)
        case PropTerm(operator='and'):
            for child in expr.children:
                if not prove_by_rewriting(child, kb, progress):
                    return False
            return True
        case PropTerm(operator='equiv'):
            # FIXME solve using equivalence substitutions
            # FIXME might be better to rewrite to (a => b) ^ (b => a) and then solve
            left = expr.children[0]
            right = expr.children[1]
            return rewrite_to_goal(left, right, kb, progress) and rewrite_to_goal(right, left, kb, progress)
        case _:
            raise RuntimeError(f"do not yet know how to prove {expr}")
