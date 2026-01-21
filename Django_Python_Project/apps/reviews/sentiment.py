# apps/reviews/sentiment.py
import warnings
import numpy as np
from pathlib import Path
from typing import Optional
import fasttext
from ml_models.aivivn_fasttext.preprocess import PreprocessText

# Monkey-patch NumPy 2.0 compatibility
_original_array = np.array
def _patched_array(*args, **kwargs):
    if 'copy' in kwargs and kwargs['copy'] is False:
        kwargs['copy'] = None
    return _original_array(*args, **kwargs)
np.array = _patched_array

# Suppress warnings
warnings.filterwarnings('ignore', message='.*copy.*', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "ml_models" / "aivivn_fasttext" / "models" / "fasttext_sentiment.bin"


class SentimentAnalyzer:
    """Singleton class để phân tích sentiment từ text + rating"""
    
    _instance = None
    _predictor = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._predictor is None:
            self._load_model()

    def _load_model(self):
        """Load FastText model"""
        try:
            if not MODEL_PATH.exists():
                print(f"[WARNING] Model không tồn tại: {MODEL_PATH}")
                self._predictor = None
                return

            self._predictor = fasttext.load_model(str(MODEL_PATH))
            self._preprocess = PreprocessText()
            print(f"[OK] Đã load sentiment model từ: {MODEL_PATH}")

        except Exception as e:
            print(f"[WARNING] Lỗi khi load model: {e}")
            self._predictor = None

    def analyze(self, text: str, rating: Optional[int] = None) -> dict:
        """
        Phân tích sentiment từ text và rating.
        
        Returns:
            dict: {
                'sentiment': 'positive' | 'negative' | 'neutral',
                'score': float (-1 đến 1),
                'text_score': float,
                'rating_score': float
            }
        """
        TEXT_WEIGHT = 0.6
        RATING_WEIGHT = 0.4
        
        # Fallback: chỉ dùng rating
        rating_score = self._rating_to_score(rating) if rating else 0.0
        
        # Nếu không có model hoặc text rỗng
        if not self._predictor or not text or not text.strip():
            return self._build_result(
                score=rating_score,
                text_score=0.0,
                rating_score=rating_score
            )
        
        # Predict sentiment từ text
        text_score = self._predict_text_score(text)
        
        # Kết hợp text + rating
        if rating:
            final_score = TEXT_WEIGHT * text_score + RATING_WEIGHT * rating_score
        else:
            final_score = text_score
        
        return self._build_result(
            score=final_score,
            text_score=text_score,
            rating_score=rating_score
        )

    def _predict_text_score(self, text: str) -> float:
        """
        Dự đoán sentiment score từ text.
        
        Returns:
            float: Score từ -1 (negative) đến 1 (positive)
        """

        # ✅ CHECK: Nếu predictor chưa load, return 0.0
        if self._predictor is None:
            return 0.0

        try:
            # Tiền xử lý
            processed_text = self._preprocess.forward(text)
            
            # Predict với k=3
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                labels, probs = self._predictor.predict(processed_text, k=3)
            
            if not labels or not probs:
                return 0.0
            
            # Value mapping
            value_map = {"0": -1.0, "1": 1.0, "2": 0.0}
            
            # Tính expected value
            text_score = 0.0
            for label, prob in zip(labels, probs):
                raw_label = label.replace("__label__", "")
                text_score += float(prob) * value_map.get(raw_label, 0.0)
            
            return text_score
            
        except Exception as e:
            print(f"[WARNING] Lỗi predict: {e}")
            return 0.0

    def _rating_to_score(self, rating: Optional[int]) -> float:
        """
        Chuyển rating (1-5) sang score (-1 đến 1).
        
        1 sao → -1.0, 3 sao → 0.0, 5 sao → 1.0
        """
        if rating is None:
            return 0.0
        rating = max(1, min(5, rating))
        return (rating - 3) / 2.0

    def _score_to_sentiment(self, score: float) -> str:
        """Chuyển score sang sentiment label"""
        if score > 0.1:
            return "positive"
        elif score < -0.1:
            return "negative"
        else:
            return "neutral"

    def _build_result(self, score: float, text_score: float, rating_score: float) -> dict:
        """Build kết quả trả về"""
        return {
            "sentiment": self._score_to_sentiment(score),
            "score": round(score, 2),
            "text_score": round(text_score, 2),
            "rating_score": round(rating_score, 2),
        }