
import abc
from collections.abc import Sequence
from typing import override


class Heuristic[N](abc.ABC):

    @abc.abstractmethod
    def rate(self, curr: N, goal: N) -> float:
        raise NotImplementedError()


class ConstantHeuristic[N](Heuristic[N]):

    def __init__(self, value: float) -> None:
        super().__init__()
        self.value = value

    @override
    def rate(self, curr: N, goal: N) -> float:
        return self.value


class WeightedHeuristic[N](Heuristic[N]):

    def __init__(self, heuristics: Sequence[tuple[float, Heuristic[N]]]) -> None:
        super().__init__()
        self.heuristics = heuristics

    @override
    def rate(self, curr: N, goal: N) -> float:
        return sum(w * h.rate(curr, goal) for w, h in self.heuristics)

