#!/usr/bin/env python3

from abc import abstractmethod
import abc
from queue import PriorityQueue
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from frozenlist import FrozenList
from typing import Sequence, assert_never, override

from infera.util import Progress
from infera.lang import Expr, Term, Var

@dataclass(frozen=True)
class Rule:
    pattern: Expr
    result: Expr
    name: str | None = None

    def __str__(self) -> str:
        return f'{self.pattern} ⊢ {self.result}'

@dataclass(frozen=True)
class TermChildIndex:
    offset: int

    def get(self, expr: Expr) -> Expr:
        assert(isinstance(expr, Term))
        return expr.children[self.offset]

    def set(self, expr: Expr, new_expr: Expr) -> Expr:
        assert(isinstance(expr, Term))
        new_children = list(expr.children)
        new_children[self.offset] = new_expr
        new_children = FrozenList(new_children)
        new_children.freeze()
        return Term(expr.operator, new_children)

    def __str__(self) -> str:
        return f'.{self.offset}'

type Index = TermChildIndex

type Path = FrozenList[Index]

def resolve(prop: Expr, path: Path) -> Expr:
    for index in path:
        prop = index.get(prop)
    return prop

def assign(root: Expr, path: Path, replace: Expr) -> Expr:
    def visit(prop: Expr, i: int) -> Expr:
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

VarSub = dict[str, Expr]

Env = dict[str, Expr]

class UnifyError(RuntimeError):
    pass

def unify(left: Expr, right: Expr) -> VarSub:
    out = VarSub()
    if isinstance(left, Var):
        out[left.name] = right
    elif isinstance(right, Var):
        out[right.name] = left
    elif isinstance(left, Term) and isinstance(right, Term) and left.operator == right.operator:
        for a, b in zip(left.children, right.children):
            out.update(unify(a, b))
    else:
        raise UnifyError()
    return out

def equal(a: Expr, b: Expr) -> bool:
    if isinstance(a, Var) and isinstance(b, Var):
        return a.name == b.name
    if isinstance(a, Term) and isinstance(b, Term) and a.operator == b.operator:
        for l, r in zip(a.children, b.children):
            if not equal(l, r):
                return False
        return True
    return False

def substitute(expr: Expr, sub: VarSub) -> Expr:
    if isinstance(expr, Var):
        return sub.get(expr.name, expr)
    if isinstance(expr, Term):
        changed = False
        new_children = []
        for child in expr.children:
            new_child = substitute(child, sub)
            if child is not new_child:
                changed = True
            new_children.append(new_child)
        new_children = FrozenList(new_children)
        new_children.freeze()
        return Term(expr.operator, new_children) if changed else expr
    assert_never(expr)

def match(prop: Expr, rule: Rule) -> Expr | None:
    try:
        sub = unify(rule.pattern, prop)
    except UnifyError:
        return None
    return substitute(rule.result, sub)

def match_all(prop: Expr, rules: list[Rule]) -> Iterator[tuple[Rule, Expr]]:
    for rule in rules:
        result = match(prop, rule)
        if result is not None:
            yield rule, result

def search_one(premise: Expr, goal: Expr, rules: list[Rule]) -> Rule | None:
    for rule, result in match_all(premise, rules):
        try:
            unify(result, goal)
        except UnifyError:
            continue
        return rule

@dataclass(order=True)
class Node:
    score: float
    expr: Expr = field(compare=False)
    rule: Rule | None = field(compare=False)
    path: Path = field(compare=False)
    parent: 'Node | None' = field(compare=False)

_empty_frozenlist = FrozenList()
_empty_frozenlist.freeze()

def enumerate_paths(prop: Expr, path: Path | None = None) -> Iterable[Path]:
    yield _empty_frozenlist
    if path is None:
        path = FrozenList()
    if isinstance(prop, Var):
        return
    if isinstance(prop, Term):
        for i, child in enumerate(prop.children):
            child_path = FrozenList([ *path, TermChildIndex(i) ])
            child_path.freeze()
            yield from enumerate_paths(child, child_path)
            yield child_path
        return
    assert_never(prop)

def size(expr: Expr) -> int:
    match expr:
        case Var(): return 1
        case Term(): return 1 + sum(size(child) for child in expr.children)
        case _: assert_never(expr)

def score(curr: Expr, goal: Expr) -> int:
    return size(curr)

def noop(_: int) -> None: pass

class Heuristic(abc.ABC):

    @abstractmethod
    def rate(self, curr: Expr, goal: Expr) -> float:
        raise NotImplementedError() 

class SizeHeuristic(Heuristic):

    @override
    def rate(self, curr: Expr, goal: Expr) -> float:
        return size(curr)

def search(
    premise: Expr,
    goal: Expr,
    rules: list[Rule],
    heuristics: Sequence[tuple[float, Heuristic]] | None = None,
    progress: Progress | None = None,
    limit: int = 0
) -> tuple[list[tuple[Expr, Rule, Path]] | None, int]:

    if heuristics is None:
        heuristics = []

    def score(x: Expr) -> float:
        return sum(w * h.rate(x, goal) for w, h in heuristics)

    count = 0
    queue = PriorityQueue[Node]()
    queue.put(Node(0, premise, None, _empty_frozenlist, None))

    # def enqueue_all(prop: Prop, rule: Rule | None = None, node: Node | None = None) -> None:
    #     for path in enumerate_paths(prop):
    #         queue.append(Node(prop, rule, path, node))

    node = None
    visited = set[tuple[Expr, Path]]()
    while queue:
        node = queue.get()
        if progress is not None:
            progress.status(f"Search iteration {count}")
        if limit > 0 and limit == count:
            raise RuntimeError(f"limit of {limit} iterations reached")
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
            for rule in rules:
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

def highlight(prop: Expr, path: Path | None) -> str:
    out = ''
    if path is not None and not path:
        out += SUB_START
    if isinstance(prop, Term):
        out += '(' + prop.operator
        for i, child in enumerate(prop.children):
            out += ' ' + highlight(child, path[1:] if path and path[0] == TermChildIndex(i) else None)
        out += ')'
    elif isinstance(prop, Var):
        out += str(prop)
    else:
        assert_never(prop)
    if path is not None and not path:
        out += SUB_END
    return out

def rewrite(
    premise: Expr,
    goal: Expr,
    rules: list[Rule],
    progress: Progress
) -> bool:
    print(f"Premise: {premise}", file=progress)
    print(f"Goal: {goal}", file=progress)
    solution, count = search(
        premise,
        goal,
        rules,
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

