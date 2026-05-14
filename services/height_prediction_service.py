from interfaces.image_classifier import ImageClassifier
from interfaces.image_preprocessor import ImagePreprocessor


class HeightPredictionService:
    def __init__(self, classifier: ImageClassifier, preprocessor: ImagePreprocessor):
        self._classifier = classifier
        self._preprocessor = preprocessor

    def _predict_digit(self, raw_input):
        tensor, preview = self._preprocessor.preprocess(raw_input)
        if tensor is None:
            return None, None, preview
        digit, confidence = self._classifier.predict(tensor)
        return digit, confidence, preview

    def predict(self, m1, m2, m3, d1, d2, d3, gender: str):
        """
        m1~m3: 엄마 키 백·십·일 자리 캔버스
        d1~d3: 아빠 키 백·십·일 자리 캔버스
        gender: "남자아이" | "여자아이"

        Returns:
            mom_digits   : [(digit, confidence), ...]  len=3, digit=None if empty
            dad_digits   : [(digit, confidence), ...]  len=3
            mom_height   : int | None
            dad_height   : int | None
            predicted    : float | None
            error        : str | None
            mom_previews : [PIL | None] * 3
            dad_previews : [PIL | None] * 3
        """
        mom_results = [self._predict_digit(c) for c in (m1, m2, m3)]
        dad_results = [self._predict_digit(c) for c in (d1, d2, d3)]

        mom_digits   = [(d, c) for d, c, _ in mom_results]
        dad_digits   = [(d, c) for d, c, _ in dad_results]
        mom_previews = [p for _, _, p in mom_results]
        dad_previews = [p for _, _, p in dad_results]

        if any(d is None for d, _ in mom_digits + dad_digits):
            return mom_digits, dad_digits, None, None, None, \
                   "모든 칸에 숫자를 그려주세요 (6칸)", mom_previews, dad_previews

        mom_height = mom_digits[0][0] * 100 + mom_digits[1][0] * 10 + mom_digits[2][0]
        dad_height = dad_digits[0][0] * 100 + dad_digits[1][0] * 10 + dad_digits[2][0]

        if gender == "남자아이":
            predicted = (dad_height + mom_height + 13) / 2
        else:
            predicted = (dad_height + mom_height - 13) / 2

        return mom_digits, dad_digits, mom_height, dad_height, predicted, \
               None, mom_previews, dad_previews
