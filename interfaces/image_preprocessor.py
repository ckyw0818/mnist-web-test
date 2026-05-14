from abc import ABC, abstractmethod
from typing import Any
import torch
from PIL import Image

class ImagePreprocessor(ABC):
    @abstractmethod
    def preprocess(self, raw_input: Any) -> tuple[torch.Tensor | None, Image.Image | None]:
        pass