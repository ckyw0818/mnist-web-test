import torch

from config import MODEL_PATH, THRESHOLD, PADDING
from domain.add_operation import AddOperation
from domain.subtract_operation import SubtractOperation
from domain.multiply_operation import MultiplyOperation
from domain.divide_operation import DivideOperation
from domain.calculator import Calculator
from infrastructure.torch_digit_classifier import TorchDigitClassifier
from infrastructure.gradio_canvas_preprocessor import GradioCanvasPreprocessor
from services.handwriting_math_service import HandwritingMathService
from ui.clear_controller import ClearController
from ui.app_builder import AppBuilder

class Container:
    def build_app(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        classifier = TorchDigitClassifier(MODEL_PATH, device)
        preprocessor = GradioCanvasPreprocessor(
            device=device,
            threshold=THRESHOLD,
            padding=PADDING
        )

        calculator = Calculator([
            AddOperation(),
            SubtractOperation(),
            MultiplyOperation(),
            DivideOperation(),
        ])

        service = HandwritingMathService(
            classifier=classifier,
            preprocessor=preprocessor,
            calculator=calculator
        )

        clear_controller = ClearController()

        builder = AppBuilder(
            service=service,
            calculator=calculator,
            clear_controller=clear_controller
        )

        return builder.build()