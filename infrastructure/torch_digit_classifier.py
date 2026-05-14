import torch
from interfaces.image_classifier import ImageClassifier
from models.mnist_cnn import MNISTCNN

class TorchDigitClassifier(ImageClassifier):
    def __init__(self, model_path: str, device: torch.device):
        self._device = device
        self._model = MNISTCNN().to(device)
        self._model.load_state_dict(torch.load(model_path, map_location=device))
        self._model.eval()

    def predict(self, image_tensor: torch.Tensor) -> tuple[int, float]:
        with torch.no_grad():
            logits = self._model(image_tensor.to(self._device))
            probs = torch.softmax(logits, dim=1)
            digit = int(torch.argmax(probs, dim=1).item())
            confidence = float(torch.max(probs).item())
            return digit, confidence