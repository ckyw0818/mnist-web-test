from interfaces.binary_operation import BinaryOperation

class SubtractOperation(BinaryOperation):
    @property
    def symbol(self) -> str:
        return "-"

    def execute(self, left: int, right: int) -> float:
        return left - right