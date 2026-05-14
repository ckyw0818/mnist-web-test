from interfaces.binary_operation import BinaryOperation

class DivideOperation(BinaryOperation):
    @property
    def symbol(self) -> str:
        return "÷"

    def execute(self, left: int, right: int) -> float:
        if right == 0:
            raise ValueError("error : devide by zero")
        return left / right