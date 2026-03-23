#!/usr/bin/env python3

from abc import abstractmethod
import abc
from queue import PriorityQueue
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from frozenlist import FrozenList
from typing import Sequence, assert_never, override

from infera.util import Progress
from ..kb import PropKB, Rule
from ..node import Index, Prop, PropTerm, PropVar, TermChildIndex


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
    # def setter(value): return value
    # prop = root
    # for index in path:
    #     if isinstance(index, NotIndex):
    #         def setter_2(value, prop=prop):
    #             assert(isinstance(prop, Not))
    #             prop.prop = value
    #         setter = setter_2
    #     elif isinstance(index, AndIndex):
    # setter(replace)


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


def match(prop: Prop, rule: Rule) -> Prop | None:
    try:
        sub = unify(rule.pattern, prop)
    except UnifyError:
        return None
    return substitute(rule.result, sub)


def match_all(prop: Prop, kb: PropKB) -> Iterator[tuple[Rule, Prop]]:
    for rule in kb.match_rules(prop):
        result = match(prop, rule)
        if result is not None:
            yield rule, result


def search_one(premise: Prop, goal: Prop, kb: PropKB) -> Rule | None:
    for rule, result in match_all(premise, kb):
        try:
            unify(result, goal)
        except UnifyError:
            continue
        return rule


@dataclass(order=True)
class Node:
    score: float
    expr: Prop = field(compare=False)
    rule: Rule | None = field(compare=False)
    path: Path = field(compare=False)
    parent: 'Node | None' = field(compare=False)


_empty_frozenlist = FrozenList()
_empty_frozenlist.freeze()


def enumerate_paths(prop: Prop, path: Path | None = None) -> Iterable[Path]:
    yield _empty_frozenlist
    if path is None:
        path = FrozenList()
    if isinstance(prop, PropVar):
        return
    if isinstance(prop, PropTerm):
        for i, child in enumerate(prop.children):
            child_path = FrozenList([ *path, TermChildIndex(i) ])
            child_path.freeze()
            yield from enumerate_paths(child, child_path)
            yield child_path
        return
    assert_never(prop)


def size(expr: Prop) -> int:
    match expr:
        case PropVar(): return 1
        case PropTerm(): return 1 + sum(size(child) for child in expr.children)
        case _: assert_never(expr)


def score(curr: Prop, goal: Prop) -> int:
    return size(curr)


def noop(_: int) -> None: pass


class Heuristic(abc.ABC):

    @abstractmethod
    def rate(self, curr: Prop, goal: Prop) -> float:
        raise NotImplementedError() 


class SizeHeuristic(Heuristic):

    @override
    def rate(self, curr: Prop, goal: Prop) -> float:
        return size(curr)


class MaxStepsExceededError(RuntimeError):

    def __init__(self, limit: int) -> None:
        super().__init__(f"limit of {limit} iterations reached")


type Step = tuple[Prop, Rule, Path]


def search(
    premise: Prop,
    goal: Prop,
    kb: PropKB,
    heuristics: Sequence[tuple[float, Heuristic]] | None = None,
    progress: Progress | None = None,
    limit: int = 0
) -> tuple[list[Step] | None, int]:

    if heuristics is None:
        heuristics = []

    def score(x: Prop) -> float:
        return sum(w * h.rate(x, goal) for w, h in heuristics)

    count = 0
    queue = PriorityQueue[Node]()
    queue.put(Node(0, premise, None, _empty_frozenlist, None))

    # def enqueue_all(prop: Prop, rule: Rule | None = None, node: Node | None = None) -> None:
    #     for path in enumerate_paths(prop):
    #         queue.append(Node(prop, rule, path, node))

    node = None
    visited = set[tuple[Prop, Path]]()
    while queue:
        node = queue.get()
        if progress is not None:
            progress.status(f"Search iteration {count}")
        if limit > 0 and limit == count:
            raise MaxStepsExceededError(limit=limit)
        count += 1
        if equal(node.expr, goal):
            break
        node_key = (node.expr, node.path)
        if node_key in visited:
            continue
        visited.add(node_key)
        print(node.expr, file=progress)
        redex = resolve(node.expr, node.path)
        for path in enumerate_paths(redex):
            redex_2 = resolve(redex, path)
            for rule in kb.match_rules(redex_2):
                new_redex = match(redex_2, rule)
                if new_redex is not None:
                    full_path = FrozenList([ *node.path, *path ])
                    full_path.freeze()
                    new_prop = assign(node.expr, full_path, new_redex)
                    queue.put(Node(score(new_prop), new_prop, rule, full_path, node))
    if node is None:
        return None, count
    out = []
    while node.parent is not None:
        out.append((node.expr, node.rule, node.path))
        node = node.parent
    out.reverse()
    return out, count


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
        heuristics=[ (1.0, SizeHeuristic()) ]
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
