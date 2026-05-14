from abc import ABC, abstractmethod
import torch

class ImageClassifier(ABC):
    @abstractmethod
    def predict(self, image_tensor: torch.Tensor) -> tuple[int, float]:
        pass