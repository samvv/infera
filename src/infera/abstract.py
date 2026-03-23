
import abc


class AbstractNode(abc.ABC):
    pass


class AbstractKB(abc.ABC):

    @abc.abstractmethod
    def add(self, node: AbstractNode, name: str | None = None) -> None:
        raise NotImplementedError()
