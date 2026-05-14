from interfaces.image_classifier import ImageClassifier
from interfaces.image_preprocessor import ImagePreprocessor
from domain.calculator import Calculator

class HandwritingMathService:
    def __init__(
        self,
        classifier: ImageClassifier,
        preprocessor: ImagePreprocessor,
        calculator: Calculator
    ):
        self._classifier = classifier
        self._preprocessor = preprocessor
        self._calculator = calculator

    def predict_digit(self, raw_input):
        tensor, preview = self._preprocessor.preprocess(raw_input)

        if tensor is None:
            return None, "Handwriting Numbers.", preview

        digit, confidence = self._classifier.predict(tensor)
        return digit, f"Prediction: {digit} (probability: {confidence:.4f})", preview

    def calculate(self, raw_input1, raw_input2, operator: str):
        digit1, msg1, preview1 = self.predict_digit(raw_input1)
        digit2, msg2, preview2 = self.predict_digit(raw_input2)

        if digit1 is None or digit2 is None:
            return (
                msg1,
                msg2,
                "not enough inputs.",
                "Write tow numbers, please.",
                preview1,
                preview2
            )

        try:
            result = self._calculator.calculate(digit1, digit2, operator)
            expr = f"{digit1} {operator} {digit2}"

            return (
                msg1,
                msg2,
                expr,
                f"result: {result}",
                preview1,
                preview2
            )
        except Exception as e:
            return (
                msg1,
                msg2,
                "Calculation error",
                str(e),
                preview1,
                preview2
            )