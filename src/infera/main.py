#!/usr/bin/env python3

import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from frozenlist import FrozenList
from typing import assert_never
from collections import deque

type Prop = And | Or | Not | Var | Int

@dataclass(frozen=True)
class Int:
    value: int

@dataclass(frozen=True)
class Var:
    name: str

    def __str__(self) -> str:
        return self.name

@dataclass(frozen=True)
class And:
    left: Prop
    right: Prop

    def __str__(self) -> str:
        left = f'({self.left})' if is_wide(self.left) else f'{self.left}'
        right = f'({self.right})' if is_wide(self.right) else f'{self.right}'
        return f'{left} ∧ {right}'

@dataclass(frozen=True)
class Equiv:
    left: Prop
    right: Prop

    def __str__(self) -> str:
        left = f'({self.left})' if is_wide(self.left) else f'{self.left}'
        right = f'({self.right})' if is_wide(self.right) else f'{self.right}'
        return f'{left} ⇔ {right}'

@dataclass(frozen=True)
class Or:
    left: Prop
    right: Prop

    def __str__(self) -> str:
        left = f'({self.left})' if is_wide(self.left) else f'{self.left}'
        right = f'({self.right})' if is_wide(self.right) else f'{self.right}'
        return f'{left} ∨ {right}'

@dataclass(frozen=True)
class Not:
    prop: Prop

    def __str__(self) -> str:
        inner = f'({self.prop})' if is_wide(self.prop) else f'{self.prop}'
        return f'¬{inner}'

def is_wide(prop: Prop) -> bool:
    return not (isinstance(prop, Var) or isinstance(prop, Not))

@dataclass(frozen=True)
class Rule:
    pattern: Prop
    result: Prop

    def __str__(self) -> str:
        return f'{self.pattern} ⊢ {self.result}'

@dataclass(frozen=True)
class NotIndex:

    def __str__(self) -> str:
        return '.prop'

    def get(self, prop: Prop) -> Prop:
        assert(isinstance(prop, Not))
        return prop.prop

    def set(self, prop: Prop, new_prop: Prop) -> Prop:
        assert(isinstance(prop, Not))
        return Not(new_prop)

@dataclass(frozen=True)
class OrIndex:
    is_left: bool

    def get(self, prop: Prop) -> Prop:
        assert(isinstance(prop, Or))
        return prop.left if self.is_left else prop.right

    def set(self, prop: Prop, new_child: Prop) -> Prop:
        assert(isinstance(prop, Or))
        return Or(new_child, prop.right) if self.is_left else And(prop.left, new_child)

    def __str__(self) -> str:
        return '.left' if self.is_left else '.right'

@dataclass(frozen=True)
class AndIndex:
    is_left: bool

    def get(self, prop: Prop) -> Prop:
        assert(isinstance(prop, And))
        return prop.left if self.is_left else prop.right

    def set(self, prop: Prop, new_child: Prop) -> Prop:
        assert(isinstance(prop, And))
        return And(new_child, prop.right) if self.is_left else And(prop.left, new_child)

    def __str__(self) -> str:
        return '.left' if self.is_left else '.right'

type Index = NotIndex | OrIndex | AndIndex

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

Env = dict[str, Prop]

class UnifyError(RuntimeError):
    pass

def unify(left: Prop, right: Prop) -> VarSub:
    out = VarSub()
    if isinstance(left, Var):
        out[left.name] = right
    elif isinstance(right, Var):
        out[right.name] = left
    elif (isinstance(left, And) and isinstance(right, And)) or (isinstance(left, Or) and isinstance(right, Or)):
        out.update(unify(left.left, right.left))
        out.update(unify(left.right, right.right))
    elif isinstance(left, Not) and isinstance(right, Not):
        out.update(unify(left.prop, right.prop))
    else:
        raise UnifyError()
    return out

def equal(a: Prop, b: Prop) -> bool:
    if isinstance(a, Var) and isinstance(b, Var):
        return a.name == b.name
    if isinstance(a, Or) and isinstance(b, Or):
        return equal(a.left, b.left) and equal(a.right, b.right)
    if isinstance(a, And) and isinstance(b, And):
        return equal(a.left, b.left) and equal(a.right, b.right)
    if isinstance(a, Not) and isinstance(b, Not):
        return equal(a.prop, b.prop)
    return False

def substitute(prop: Prop, sub: VarSub) -> Prop:
    if isinstance(prop, Var):
        return sub.get(prop.name, prop)
    if isinstance(prop, Or):
        return Or(substitute(prop.left, sub), substitute(prop.right, sub))
    if isinstance(prop, And):
        return And(substitute(prop.left, sub), substitute(prop.right, sub))
    if isinstance(prop, Not):
        return Not(substitute(prop.prop, sub))
    assert_never(prop)

def match(prop: Prop, rule: Rule) -> Prop | None:
    try:
        sub = unify(rule.pattern, prop)
    except UnifyError:
        return None
    return substitute(rule.result, sub)

def match_all(prop: Prop, rules: list[Rule]) -> Iterator[tuple[Rule, Prop]]:
    for rule in rules:
        result = match(prop, rule)
        if result is not None:
            yield rule, result

def solve_one(premise: Prop, goal: Prop, rules: list[Rule]) -> Rule | None:
    for rule, result in match_all(premise, rules):
        try:
            unify(result, goal)
        except UnifyError:
            continue
        return rule

@dataclass
class Node:
    prop: Prop
    rule: Rule | None
    path: Path
    parent: 'Node | None'

_empty_frozenlist = FrozenList()
_empty_frozenlist.freeze()

def enumerate_paths(prop: Prop, path: Path | None = None) -> Iterable[Path]:
    yield _empty_frozenlist
    if path is None:
        path = FrozenList()
    if isinstance(prop, Var):
        return
    if isinstance(prop, Or):
        left = FrozenList([ *path, OrIndex(True) ])
        right = FrozenList([ *path, OrIndex(False) ])
        left.freeze()
        right.freeze()
        yield from enumerate_paths(prop.left, left)
        yield from enumerate_paths(prop.right, right)
        yield left
        yield right
        return
    if isinstance(prop, And):
        left = FrozenList([ *path, AndIndex(True) ])
        right = FrozenList([ *path, AndIndex(False) ])
        left.freeze()
        right.freeze()
        yield from enumerate_paths(prop.left, left)
        yield from enumerate_paths(prop.right, right)
        yield left
        yield right
        return
    if isinstance(prop, Not):
        child = FrozenList([ *path, NotIndex() ])
        child.freeze()
        yield child
        return
    assert_never(prop)

def solve_many(premise: Prop, goal: Prop, rules: list[Rule]) -> tuple[list[tuple[Prop, Rule, Path]] | None, int]:

    count = 0
    queue = deque[Node]([ Node(premise, None, _empty_frozenlist, None) ])

    # def enqueue_all(prop: Prop, rule: Rule | None = None, node: Node | None = None) -> None:
    #     for path in enumerate_paths(prop):
    #         queue.append(Node(prop, rule, path, node))

    node = None
    visited = set[tuple[Prop, Path]]()
    while queue:
        node = queue.popleft()
        count += 1
        if equal(node.prop, goal):
            break
        print(node.prop)
        node_key = (node.prop, node.path)
        if node_key in visited:
            continue
        visited.add(node_key)
        redex = resolve(node.prop, node.path)
        for path in enumerate_paths(redex):
            redex_2 = resolve(redex, path)
            for rule in rules:
                new_redex = match(redex_2, rule)
                if new_redex is not None:
                    full_path = FrozenList([ *node.path, *path ])
                    full_path.freeze()
                    new_prop = assign(node.prop, full_path, new_redex)
                    queue.append(Node(new_prop, rule, full_path, node))
    if node is None:
        return None, count
    out = []
    while node.parent is not None:
        out.append((node.prop, node.rule, node.path))
        node = node.parent
    out.reverse()
    return out, count

SUB_START = '\033[1m\033[92m'
SUB_END   = '\033[0m'

def highlight(prop: Prop, path: Path | None) -> str:
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

if __name__ == '__main__':
    rules = [
        Rule(
            Var('a'),
            Not(Not(Var('a'))),
        ),
        Rule(
            Not(Or(Var('a'), Var('b'))),
            And(Not(Var('a')), Not(Var('b'))),
        ),
        Rule(
            And(Not(Var('a')), Not(Var('b'))),
            Not(Or(Var('a'), Var('b'))),
        ),
        Rule(
            And(Var('a'), Var('b')),
            And(Var('b'), Var('a')),
        ),
        Rule(
            And(Var('b'), Var('a')),
            And(Var('a'), Var('b')),
        ),
    ]
    premise = And(Not(Or(Var('d'), Var('c'))), Var('k'))
    goal = And(And(Not(Not(Not(Var('c')))), Not(Var('d'))), Var('k'))
    # premise = Or(Var('a'), Var('b'))
    # goal = Not(Not(Or(Var('a'), Var('b'))))
    print(f"Premise: {premise}")
    print(f"Goal: {goal}")
    solution, count = solve_many(premise, goal, rules)
    print(f"Searched {count} states")
    if solution is None:
        print("Formula could not be solved.")
        sys.exit(1)
    print("Steps:")
    last = premise
    for i, (prop, rule, path) in enumerate(solution):
        print(f"{i+1}. {highlight(last, path)} ⇒ {prop} by rule {SUB_START}{rule.pattern}{SUB_END} ⊢ {rule.result}")
        last = prop
