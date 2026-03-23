
from dataclasses import dataclass
from frozenlist import FrozenList


type Node = Term | Formula


class NodeBase:
    pass


type Term = Var | Function


@dataclass(frozen=True)
class Var(NodeBase):
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Function(NodeBase):
    name: str
    args: FrozenList[Term]

    def __str__(self) -> str:
        out = '('
        out += self.name
        for child in self.args:
            out += ' ' + str(child)
        out += ')'
        return out


type Formula = Predicate | Connected | Quantized


@dataclass(frozen=True)
class Predicate(NodeBase):
    name: str
    args: FrozenList[Connected]

    def __str__(self) -> str:
        out = '('
        out += self.name
        for child in self.args:
            out += ' ' + str(child)
        out += ')'
        return out


@dataclass(frozen=True)
class Quantized(NodeBase):
    name: str
    bexprinders: FrozenList[Var]
    predicate: Predicate


@dataclass(frozen=True)
class Connected(NodeBase):
    operator: str
    children: FrozenList[Formula]

    @property
    def arity(self) -> int:
        return len(self.children)

    def __str__(self) -> str:
        out = '('
        out += self.operator
        for child in self.children:
            out += ' ' + str(child)
        out += ')'
        return out

