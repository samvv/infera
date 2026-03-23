
import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from infera.lang.pred.node import Pred
    from infera.lang.prop.node import Prop


type Node = Prop | Pred


class AbstractKB(abc.ABC):

    @abc.abstractmethod
    def add(self, node: Node, name: str | None = None) -> None:
        raise NotImplementedError()
