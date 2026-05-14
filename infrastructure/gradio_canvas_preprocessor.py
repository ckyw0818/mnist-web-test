from typing import Any
import numpy as np
import torch
from PIL import Image, ImageOps
from interfaces.image_preprocessor import ImagePreprocessor

class GradioCanvasPreprocessor(ImagePreprocessor):
    def __init__(self, device: torch.device, threshold: int, padding: int):
        self._device = device
        self._threshold = threshold
        self._padding = padding

    def preprocess(self, raw_input: Any) -> tuple[torch.Tensor | None, Image.Image | None]:
        source = self._extract_handwriting_image(raw_input)
        if source is None:
            return None, None

        pil_img = self._to_pil(source)
        if pil_img is None:
            return None, None

        pil_img = pil_img.convert("L")
        pil_img = ImageOps.invert(pil_img)
        pil_img = self._crop_to_content(pil_img)
        pil_img = self._make_square(pil_img)
        pil_img = pil_img.resize((28, 28))

        arr = np.array(pil_img).astype(np.float32) / 255.0

        if arr.max() < 0.05:
            return None, pil_img

        tensor = (
            torch.tensor(arr, dtype=torch.float32)
            .unsqueeze(0)
            .unsqueeze(0)
            .to(self._device)
        )
        return tensor, pil_img

    def _extract_handwriting_image(self, raw_input: Any):
        if raw_input is None:
            return None

        if not isinstance(raw_input, dict):
            return None

        composite = raw_input.get("composite")
        if composite is not None:
            return composite

        return None

    def _to_pil(self, image: Any):
        if isinstance(image, np.ndarray):
            return Image.fromarray(image)
        if isinstance(image, Image.Image):
            return image
        return None

    def _crop_to_content(self, pil_img: Image.Image) -> Image.Image:
        arr = np.array(pil_img)
        ys, xs = np.where(arr > self._threshold)

        if len(xs) == 0 or len(ys) == 0:
            return pil_img

        x_min = max(0, xs.min() - self._padding)
        x_max = min(arr.shape[1], xs.max() + self._padding)
        y_min = max(0, ys.min() - self._padding)
        y_max = min(arr.shape[0], ys.max() + self._padding)

        return pil_img.crop((x_min, y_min, x_max, y_max))

    def _make_square(self, pil_img: Image.Image) -> Image.Image:
        w, h = pil_img.size
        side = max(w, h) + 20
        square = Image.new("L", (side, side), color=0)
        square.paste(pil_img, ((side - w) // 2, (side - h) // 2))
        return square