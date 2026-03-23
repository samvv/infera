
from dataclasses import dataclass
from frozenlist import FrozenList


type Pred = PredTerm | PredFormula


class PredBase:
    pass


type PredTerm = PredVar | PredFunction


@dataclass(frozen=True)
class PredVar(PredBase):
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class PredFunction(PredBase):
    name: str
    args: FrozenList[PredTerm]

    def __str__(self) -> str:
        out = '('
        out += self.name
        for child in self.args:
            out += ' ' + str(child)
        out += ')'
        return out


type PredFormula = PredPredicate | PredConnective | PredQuantized


@dataclass(frozen=True)
class PredPredicate(PredBase):
    name: str
    args: FrozenList[PredConnective]

    def __str__(self) -> str:
        out = '('
        out += self.name
        for child in self.args:
            out += ' ' + str(child)
        out += ')'
        return out


@dataclass(frozen=True)
class PredQuantized(PredBase):
    name: str
    bexprinders: FrozenList[PredVar]
    predicate: PredPredicate


@dataclass(frozen=True)
class PredConnective(PredBase):
    operator: str
    children: FrozenList[PredFormula]

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

