# apps/reviews/sentiment.py
import fasttext
from pathlib import Path
from ml_models.aivivn_fasttext.preprocess import PreprocessText

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
                print(f"⚠️  Model không tồn tại: {MODEL_PATH}")
                print("   Hãy chạy train.py để tạo model!")
                self._predictor = None
                return

            self._predictor = fasttext.load_model(str(MODEL_PATH))
            self._preprocess = PreprocessText()
            print(f"✓ Đã load sentiment model từ: {MODEL_PATH}")

        except Exception as e:
            print(f"⚠️  Lỗi khi load model: {e}")
            self._predictor = None

    def analyze(self, text: str) -> dict:
        """
        Phân tích sentiment của text

        Args:
            text: Nội dung đánh giá

        Returns:
            dict: {
                'sentiment': 'positive' | 'negative' | 'neutral',
                'score': 0.95,  # Độ tin cậy (0-1)
                'label': '1' | '0' | 'unknown'
            }
        """
        # Nếu model chưa load hoặc text rỗng
        if self._predictor is None:
            return {"sentiment": "neutral", "score": 0.0, "label": "unknown"}

        if not text or not text.strip():
            return {"sentiment": "neutral", "score": 0.0, "label": "unknown"}

        try:
            # Tiền xử lý text
            processed_text = self._preprocess.forward(text)

            # Dự đoán
            labels, probs = self._predictor.predict(processed_text, k=1)

            # Kiểm tra kết quả
            if not labels or not probs:
                return {"sentiment": "neutral", "score": 0.0, "label": "unknown"}

            # Parse kết quả
            label = labels[0].replace("__label__", "")
            confidence = float(probs[0])

            # Map label sang sentiment
            sentiment_map = {
                "1": "positive",
                "0": "negative",
            }

            sentiment = sentiment_map.get(label, "neutral")

            return {"sentiment": sentiment, "score": confidence, "label": label}

        except Exception as e:
            print(f"⚠️  Lỗi khi phân tích sentiment: {e}")
            return {"sentiment": "neutral", "score": 0.0, "label": "unknown"}