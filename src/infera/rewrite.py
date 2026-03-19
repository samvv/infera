#!/usr/bin/env python3

from queue import PriorityQueue
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from frozenlist import FrozenList
from typing import assert_never
from collections import deque

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

def solve_one(premise: Expr, goal: Expr, rules: list[Rule]) -> Rule | None:
    for rule, result in match_all(premise, rules):
        try:
            unify(result, goal)
        except UnifyError:
            continue
        return rule

@dataclass(order=True)
class Node:
    score: int
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

def solve_many(premise: Expr, goal: Expr, rules: list[Rule]) -> tuple[list[tuple[Expr, Rule, Path]] | None, int]:

    count = 0
    queue = PriorityQueue()
    queue.put(Node(0, premise, None, _empty_frozenlist, None))

    # def enqueue_all(prop: Prop, rule: Rule | None = None, node: Node | None = None) -> None:
    #     for path in enumerate_paths(prop):
    #         queue.append(Node(prop, rule, path, node))

    node = None
    visited = set[tuple[Expr, Path]]()
    while queue:
        node = queue.get()
        count += 1
        if equal(node.expr, goal):
            break
        print(node.expr)
        node_key = (node.expr, node.path)
        if node_key in visited:
            continue
        visited.add(node_key)
        redex = resolve(node.expr, node.path)
        for path in enumerate_paths(redex):
            redex_2 = resolve(redex, path)
            for rule in rules:
                new_redex = match(redex_2, rule)
                if new_redex is not None:
                    full_path = FrozenList([ *node.path, *path ])
                    full_path.freeze()
                    new_prop = assign(node.expr, full_path, new_redex)
                    queue.put(Node(score(new_prop, goal), new_prop, rule, full_path, node))
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
    if isinstance(prop, And):
        left = highlight(prop.left, path[1:] if path and path[0] == AndIndex(True) else None)
        if is_wide(prop.left):
            left = f'({left})'
        right = highlight(prop.right, path[1:] if path and path[0] == AndIndex(False) else None)
        if is_wide(prop.right):
            right = f'({right})'
        out += f'{left} ∧ {right}'
    elif isinstance(prop, Or):
        left = highlight(prop.left, path[1:] if path and path[0] == AndIndex(True) else None)
        if is_wide(prop.left):
            left = f'({left})'
        right = highlight(prop.right, path[1:] if path and path[0] == AndIndex(False) else None)
        if is_wide(prop.right):
            right = f'({right})'
        out += f'{left} ∨ {right}'
    elif isinstance(prop, Var):
        out += str(prop)
    elif isinstance(prop, Not):
        child = highlight(prop.prop, path[1:] if path and path[0] == NotIndex() else None)
        if is_wide(prop.prop):
            child = f'({child})'
        out += f'¬{child}'
    else:
        assert_never(prop)
    if path is not None and not path:
        out += SUB_END
    return out

def rewrite(premise: Expr, goal: Expr, rules: list[Rule]) -> bool:
    print(f"Premise: {premise}")
    print(f"Goal: {goal}")
    solution, count = solve_many(premise, goal, rules)
    print(f"Searched {count} states")
    if solution is None:
        print("Formula could not be solved.")
        return False
    print("Steps:")
    last = premise
    for i, (prop, rule, path) in enumerate(solution):
        print(f"{i+1}. {highlight(last, path)} ⇒ {prop} by rule {SUB_START}{rule.pattern}{SUB_END} ⊢ {rule.result}")
        last = prop
    return True

