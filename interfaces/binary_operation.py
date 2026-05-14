from abc import ABC, abstractmethod

class BinaryOperation(ABC):
    @property
    @abstractmethod
    def symbol(self) -> str:
        pass

    @abstractmethod
    def execute(self, left: int, right: int) -> float:
        pass