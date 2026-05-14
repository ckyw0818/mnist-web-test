from interfaces.binary_operation import BinaryOperation

class Calculator:
    def __init__(self, operations: list[BinaryOperation]):
        self._operations = {op.symbol: op for op in operations}

    def calculate(self, left: int, right: int, operator: str) -> float:
        operation = self._operations.get(operator)
        if operation is None:
            raise ValueError(f"Unsupported operator: {operator}")
        return operation.execute(left, right)

    def supported_symbols(self) -> list[str]:
        return list(self._operations.keys())