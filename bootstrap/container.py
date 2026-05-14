import torch

from config import MODEL_PATH, THRESHOLD, PADDING
from infrastructure.torch_digit_classifier import TorchDigitClassifier
from infrastructure.gradio_canvas_preprocessor import GradioCanvasPreprocessor
from services.height_prediction_service import HeightPredictionService
from ui.app_builder import AppBuilder


class Container:
    def build_app(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        classifier = TorchDigitClassifier(MODEL_PATH, device)
        preprocessor = GradioCanvasPreprocessor(
            device=device,
            threshold=THRESHOLD,
            padding=PADDING,
        )

        service = HeightPredictionService(
            classifier=classifier,
            preprocessor=preprocessor,
        )

        builder = AppBuilder(service=service)
        return builder.build()
