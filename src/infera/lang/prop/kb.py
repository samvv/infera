

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import assert_never, override

from infera.abstract import AbstractKB, AbstractNode

from .node import PropTerm, Prop, PropVar


def symbols(prop: Prop) -> Iterable[str]:
    match prop:
        case PropVar():
            yield '*'
        case PropTerm():
            yield prop.operator
            for child in prop.children:
                yield from symbols(child)
        case _:
            assert_never(prop)


class DNode[T]:

    def __init__(self) -> None:
        self.children = dict[str, DNode]()
        self.value: list[T] = []


class DTree[T]:

    def __init__(self) -> None:
        self.root = None

    def add(self, expr: Prop, value: T) -> None:
        if not self.root:
            self.root = DNode()
        node = self.root
        for symbol in symbols(expr):
            if symbol in node.children:
                node = node.children[symbol]
            else:
                next = DNode()
                node.children[symbol] = next
                node = next
        node.value.append(value)

    def lookup(self, pattern: Prop) -> Sequence[Rule]:
        if self.root is None:
            return []
        node = self.root
        for symbol in symbols(pattern):
            if symbol not in node.children:
                return []
            node = node.children[symbol]
        return node.value


@dataclass(frozen=True)
class Rule:
    pattern: Prop
    result: Prop
    name: str | None = None

    def __str__(self) -> str:
        return self.name or f'{self.pattern} ⊢ {self.result}'


class PropKB(AbstractKB):

    def __init__(self) -> None:
        self._matcher = DTree()
        self._rules = list[Rule]()
        self._rules_by_name = dict[str, Rule]()

    def _add_rule(self, rule: Rule) -> None:
        self._rules.append(rule)
        self._matcher.add(rule.pattern, rule)
        if rule.name is not None:
            self._rules_by_name[rule.name] = rule

    @override
    def add(self, node: AbstractNode, name: str | None = None) -> None:
        match node:
           case PropTerm(operator='implies'):
               premise = node.children[0]
               goal = node.children[1]
               self._add_rule(Rule(premise, goal, name))
           case PropTerm(operator='equiv'):
               left = node.children[0]
               right = node.children[1]
               self._add_rule(Rule(left, right, name))
               self._add_rule(Rule(right, left, name))
           case PropTerm(operator='and'):
               for i, child in enumerate(node.children):
                   self.add(child, name and f'{name}_{i}')
           case _:
               raise RuntimeError(f"did not yet know how to add proven {node} to the KB")

    def match_rules(self, prop: Prop) -> Iterable[Rule]:
        print("SEEK")
        print(prop)
        print("FIND")
        for r in self._matcher.lookup(prop):
            print(str(r))
        return self._matcher.lookup(prop)

    def count_rules(self) -> int:
        return len(self._rules)

    def get_rule_by_name(self, name: str) -> Rule | None:
        return self._rules_by_name.get(name)

    @property
    def rules(self) -> Iterable[Rule]:
        return iter(self._rules)
