

from collections.abc import Iterable
from dataclasses import dataclass
from typing import override

from infera.abstract import AbstractKB

from .node import PropTerm, Prop


@dataclass(frozen=True)
class Rule:
    pattern: Prop
    result: Prop
    name: str | None = None

    def __str__(self) -> str:
        return f'{self.pattern} ⊢ {self.result}'


class PropKB(AbstractKB):

    def __init__(self) -> None:
        self._rules = list[Rule]()
        self._rules_by_name = dict[str, Rule]()

    def _add_rule(self, rule: Rule) -> None:
        self._rules.append(rule)
        if rule.name is not None:
            self._rules_by_name[rule.name] = rule

    @override
    def add(self, node: Prop, name: str | None = None) -> None:
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

    def count_rules(self) -> int:
        return len(self._rules)

    def get_rule(self, name: str) -> Rule | None:
        return self._rules_by_name.get(name)

    @property
    def rules(self) -> Iterable[Rule]:
        return iter(self._rules)
