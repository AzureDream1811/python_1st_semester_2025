# apps/reviews/sentiment.py
import warnings
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
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
    """Singleton class để phân tích sentiment từ text + rating với conflict detection"""
    
    _instance = None
    _predictor = None

    # Thresholds
    CONFLICT_THRESHOLD = 1.2  # Gap giữa text_score và rating_score
    SHORT_TEXT_LENGTH = 20    # Text ngắn (chars)
    LONG_TEXT_LENGTH = 100    # Text dài
    LOW_CONFIDENCE = 0.5      # Confidence thấp
    HIGH_CONFIDENCE = 0.85    # Confidence cao

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
        Phân tích sentiment từ text và rating với adaptive weighting.
        
        Returns:
            dict: {
                'sentiment': 'positive' | 'negative' | 'neutral',
                'score': float (-1 đến 1),
                'text_score': float,
                'rating_score': float,
                'confidence': float,
                'conflict': bool,
                'source': str  # 'text', 'rating', hoặc 'combined'
            }
        """
        # Fallback: chỉ dùng rating
        rating_score = self._rating_to_score(rating) if rating else 0.0
        
        # Nếu không có model hoặc text rỗng
        if not self._predictor or not text or not text.strip():
            return self._build_result(
                score=rating_score,
                text_score=0.0,
                rating_score=rating_score,
                confidence=1.0 if rating else 0.0,
                conflict=False,
                source='rating' if rating else 'none'
            )
        
        # Predict sentiment từ text
        text_score, text_confidence = self._predict_text_score(text)
        text_length = len(text.strip())
        
        # Case 1: Không có rating → chỉ dùng text
        if not rating:
            return self._build_result(
                score=text_score,
                text_score=text_score,
                rating_score=0.0,
                confidence=text_confidence,
                conflict=False,
                source='text'
            )
        
        # Case 2: Có cả text và rating → adaptive weighting
        text_weight, rating_weight = self._calculate_adaptive_weights(
            text_length, text_confidence
        )
        
        # Kết hợp text + rating
        final_score = text_weight * text_score + rating_weight * rating_score
        
        # Detect conflict
        conflict = self._detect_conflict(text_score, rating_score)
        
        # Nếu conflict → ưu tiên text (nếu text đủ dài và confidence cao)
        if conflict and text_length > self.SHORT_TEXT_LENGTH and text_confidence > self.LOW_CONFIDENCE:
            final_score = text_score
            source = 'text_priority'
            print(f"[CONFLICT] Text={text_score:.2f} vs Rating={rating_score:.2f} → Ưu tiên text")
        else:
            source = 'combined'
        
        return self._build_result(
            score=final_score,
            text_score=text_score,
            rating_score=rating_score,
            confidence=text_confidence,
            conflict=conflict,
            source=source
        )

    def _predict_text_score(self, text: str) -> Tuple[float, float]:
        """
        Dự đoán sentiment score từ text.
        
        Returns:
            tuple: (score, confidence)
                - score: -1 (negative) đến 1 (positive)
                - confidence: 0 đến 1
        """
        if self._predictor is None:
            return 0.0, 0.0

        try:
            # Tiền xử lý
            processed_text = self._preprocess.forward(text)
            
            # Predict với k=3
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                labels, probs = self._predictor.predict(processed_text, k=3)
            
            # Kiểm tra kết quả (xử lý cả list và numpy array)
            if len(labels) == 0 or len(probs) == 0:
                return 0.0, 0.0
            
            # Chuyển sang list để tránh lỗi numpy array ambiguity
            labels = list(labels) if hasattr(labels, '__iter__') else [labels]
            probs = list(probs) if hasattr(probs, '__iter__') else [probs]

            # Normalize probabilities (trong trường hợp model chỉ trả về < 3 labels)
            total_prob = sum(probs)
            if total_prob > 0:
                probs = [p / total_prob for p in probs]

            # Value mapping
            value_map = {"0": -1.0, "1": 1.0, "2": 0.0}
            
            # Tính expected value
            text_score = 0.0
            for label, prob in zip(labels, probs):
                raw_label = label.replace("__label__", "")
                text_score += float(prob) * value_map.get(raw_label, 0.0)
            
            # Confidence = probability của label cao nhất
            confidence = float(max(probs)) if len(probs) > 0 else 0.0

            return text_score, confidence
            
        except Exception as e:
            print(f"[WARNING] Lỗi predict: {e}")
            return 0.0, 0.0

    def _calculate_adaptive_weights(self, text_length: int, confidence: float) -> Tuple[float, float]:
        """
        Tính toán weights động dựa trên text length và confidence.
        
        Logic:
        - Text dài + confidence cao → text_weight cao (0.75)
        - Text ngắn hoặc confidence thấp → rating_weight cao (0.6)
        - Default: 0.6 text, 0.4 rating
        """
        base_text_weight = 0.6
        
        # Text dài và confidence cao → tăng text weight
        if text_length > self.LONG_TEXT_LENGTH and confidence > self.HIGH_CONFIDENCE:
            text_weight = 0.75
        
        # Text ngắn hoặc confidence thấp → giảm text weight
        elif text_length < self.SHORT_TEXT_LENGTH or confidence < self.LOW_CONFIDENCE:
            text_weight = 0.4
        
        # Medium case
        else:
            text_weight = base_text_weight
        
        rating_weight = 1.0 - text_weight
        return text_weight, rating_weight

    def _detect_conflict(self, text_score: float, rating_score: float) -> bool:
        """
        Phát hiện conflict giữa text sentiment và rating.
        
        Returns:
            bool: True nếu có conflict đáng kể
        """
        gap = abs(text_score - rating_score)
        return gap > self.CONFLICT_THRESHOLD

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

    def _build_result(
        self, 
        score: float, 
        text_score: float, 
        rating_score: float,
        confidence: float,
        conflict: bool,
        source: str
    ) -> dict:
        """Build kết quả trả về"""
        sentiment = self._score_to_sentiment(score)
        # Map sentiment to label: positive=1, negative=0, neutral=unknown
        label_map = {"positive": "1", "negative": "0", "neutral": "unknown"}
        return {
            "sentiment": sentiment,
            "score": float(round(float(score), 2)),
            "text_score": float(round(float(text_score), 2)),
            "rating_score": float(round(float(rating_score), 2)),
            "confidence": float(round(float(confidence), 2)),
            "conflict": bool(conflict),
            "source": str(source),  # text, rating, combined, text_priority, none
            "label": label_map.get(sentiment, "unknown"),
        }