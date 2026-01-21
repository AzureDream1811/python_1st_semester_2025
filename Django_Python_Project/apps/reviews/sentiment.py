# apps/reviews/sentiment.py
import warnings
import numpy as np
from pathlib import Path
from typing import Optional
# Import fasttext sau khi patch
import fasttext
from ml_models.aivivn_fasttext.preprocess import PreprocessText

# Monkey-patch để fix NumPy 2.0 compatibility với FastText
# FastText sử dụng np.array(obj, copy=False) nhưng NumPy 2.0 không cho phép
_original_array = np.array

def _patched_array(*args, **kwargs):
    """Patch np.array để xử lý copy=False trong NumPy 2.0"""
    if 'copy' in kwargs and kwargs['copy'] is False:
        kwargs['copy'] = None  # NumPy 2.0 dùng None thay vì False
    return _original_array(*args, **kwargs)

np.array = _patched_array



# Suppress các warning không cần thiết
warnings.filterwarnings('ignore', message='.*copy.*', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# Xác định đường dẫn model từ vị trí hiện tại
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Django_Python_Project/
MODEL_PATH = (
    BASE_DIR / "ml_models" / "aivivn_fasttext" / "models" / "fasttext_sentiment.bin"
)


class SentimentAnalyzer:
    """
    Singleton class để load model 1 lần duy nhất
    Tránh load lại model mỗi lần phân tích
    """

    _instance = None
    _predictor = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Khởi tạo predictor nếu chưa có"""
        if self._predictor is None:
            self._load_model()

    def _load_model(self):
        """Load FastText model"""
        try:
            if not MODEL_PATH.exists():
                print(f"[WARNING] Model khong ton tai: {MODEL_PATH}")
                print("   Hay chay train.py de tao model!")
                self._predictor = None
                return

            self._predictor = fasttext.load_model(str(MODEL_PATH))
            self._preprocess = PreprocessText()
            print(f"[OK] Da load sentiment model tu: {MODEL_PATH}")

        except Exception as e:
            print(f"[WARNING] Loi khi load model: {e}")
            self._predictor = None

    def analyze(self, text: str, rating: Optional[int] = None) -> dict:
        """
        Phân tích sentiment của text, kết hợp với star rating nếu có.

        Sử dụng weighted average để kết hợp:
        - Text sentiment score (từ model AI)
        - Rating score (chuyển đổi từ 1-5 sao sang -1 đến 1)

        Công thức: final_score = TEXT_WEIGHT × text_score + RATING_WEIGHT × rating_score

        Args:
            text: Nội dung đánh giá
            rating: Số sao đánh giá (1-5), optional

        Returns:
            dict: {
                'sentiment': 'positive' | 'negative' | 'neutral',
                'score': float,  # Điểm sentiment cuối cùng (-1 đến 1)
                'label': '1' | '0' | 'unknown',
                'text_score': float,  # Điểm từ phân tích text
                'rating_score': float,  # Điểm từ star rating
            }
        """
        # Trọng số kết hợp (text chiếm 60%, rating chiếm 40%)
        TEXT_WEIGHT = 0.6
        RATING_WEIGHT = 0.4

        # Nếu model chưa load hoặc text rỗng
        if self._predictor is None:
            # Fallback: chỉ dùng rating nếu có
            if rating is not None:
                rating_score = self._rating_to_score(rating)
                sentiment = self._score_to_sentiment(rating_score)
                return {
                    "sentiment": sentiment,
                    "score": rating_score,
                    "label": "unknown",
                    "text_score": 0.0,
                    "rating_score": rating_score,
                }
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "label": "unknown",
                "text_score": 0.0,
                "rating_score": 0.0,
            }

        if not text or not text.strip():
            # Fallback: chỉ dùng rating nếu có
            if rating is not None:
                rating_score = self._rating_to_score(rating)
                sentiment = self._score_to_sentiment(rating_score)
                return {
                    "sentiment": sentiment,
                    "score": rating_score,
                    "label": "unknown",
                    "text_score": 0.0,
                    "rating_score": rating_score,
                }
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "label": "unknown",
                "text_score": 0.0,
                "rating_score": 0.0,
            }

        try:
            # Tiền xử lý text
            processed_text = self._preprocess.forward(text)

            # Dự đoán - suppress NumPy 2.0 warning
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=DeprecationWarning)
                warnings.filterwarnings('ignore', message='.*copy.*')
                try:
                    labels, probs = self._predictor.predict(processed_text, k=1)
                except ValueError as ve:
                    # NumPy 2.0 copy error - try alternative approach
                    if 'copy' in str(ve):
                        # Fallback: dùng rating nếu có
                        if rating is not None:
                            rating_score = self._rating_to_score(rating)
                            sentiment = self._score_to_sentiment(rating_score)
                            return {
                                "sentiment": sentiment,
                                "score": rating_score,
                                "label": "fallback",
                                "text_score": 0.0,
                                "rating_score": rating_score,
                            }
                        return {
                            "sentiment": "neutral",
                            "score": 0.0,
                            "label": "fallback",
                            "text_score": 0.0,
                            "rating_score": 0.0,
                        }
                    raise

            # Kiểm tra kết quả
            if not labels or not probs:
                if rating is not None:
                    rating_score = self._rating_to_score(rating)
                    sentiment = self._score_to_sentiment(rating_score)
                    return {
                        "sentiment": sentiment,
                        "score": rating_score,
                        "label": "unknown",
                        "text_score": 0.0,
                        "rating_score": rating_score,
                    }
                return {
                    "sentiment": "neutral",
                    "score": 0.0,
                    "label": "unknown",
                    "text_score": 0.0,
                    "rating_score": 0.0,
                }

            # Parse kết quả
            label = labels[0].replace("__label__", "")
            confidence = float(probs[0])

            # Chuyển đổi text prediction sang score (-1 đến 1)
            # label "1" = positive, label "0" = negative
            if label == "1":
                text_score = confidence  # positive: 0 đến 1
            else:
                text_score = -confidence  # negative: -1 đến 0

            # Tính rating score nếu có
            rating_score = 0.0
            if rating is not None:
                rating_score = self._rating_to_score(rating)
                # Kết hợp text và rating với trọng số
                final_score = TEXT_WEIGHT * text_score + RATING_WEIGHT * rating_score
            else:
                # Không có rating, chỉ dùng text
                final_score = text_score

            # Xác định sentiment từ final score
            sentiment = self._score_to_sentiment(final_score)

            return {
                "sentiment": sentiment,
                "score": final_score,
                "label": label,
                "text_score": text_score,
                "rating_score": rating_score,
            }

        except Exception as e:
            print(f"[WARNING] Loi khi phan tich sentiment: {e}")
            # Fallback: dùng rating nếu có
            if rating is not None:
                rating_score = self._rating_to_score(rating)
                sentiment = self._score_to_sentiment(rating_score)
                return {
                    "sentiment": sentiment,
                    "score": rating_score,
                    "label": "unknown",
                    "text_score": 0.0,
                    "rating_score": rating_score,
                }
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "label": "unknown",
                "text_score": 0.0,
                "rating_score": 0.0,
            }

    def _rating_to_score(self, rating: Optional[int]) -> float:
        """
        Chuyển đổi star rating (1-5) sang score (-1 đến 1).

        Công thức: score = (rating - 3) / 2
        - 1 sao → -1.0 (rất tiêu cực)
        - 2 sao → -0.5 (tiêu cực)
        - 3 sao →  0.0 (trung lập)
        - 4 sao →  0.5 (tích cực)
        - 5 sao →  1.0 (rất tích cực)
        """
        if rating is None:
            return 0.0
        # Clamp rating to 1-5 range
        rating = max(1, min(5, rating))
        return (rating - 3) / 2.0

    def _score_to_sentiment(self, score: float) -> str:
        """
        Chuyển đổi score (-1 đến 1) sang sentiment label.

        - score > 0.2: positive
        - score < -0.2: negative
        - else: neutral
        """
        if score > 0.2:
            return "positive"
        elif score < -0.2:
            return "negative"
        else:
            return "neutral"