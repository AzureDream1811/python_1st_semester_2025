"""
Sentiment Analyzer wrapper cho reviews app
Sử dụng Singleton pattern để load model một lần
"""
import os
from pathlib import Path


class SentimentAnalyzer:
    """Singleton class để phân tích sentiment"""

    _instance = None
    _model = None
    _preprocessor = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        """Load FastText model và preprocessor"""
        try:
            from ml_models.aivivn_fasttext.preprocess import PreprocessText
            from ml_models.aivivn_fasttext.config import MODEL_DIR
            import fasttext

            model_path = MODEL_DIR / "fasttext_sentiment.bin"

            if model_path.exists():
                self._model = fasttext.load_model(str(model_path))
                self._preprocessor = PreprocessText()
            else:
                print(f"Warning: Model not found at {model_path}")
                self._model = None
                self._preprocessor = None
        except Exception as e:
            print(f"Error loading sentiment model: {e}")
            self._model = None
            self._preprocessor = None

    def analyze(self, text: str) -> dict:
        """
        Phân tích sentiment của text
        
        Returns:
            dict: {
                'sentiment': 'positive' | 'negative' | 'neutral',
                'score': float (-1 to 1),
                'processed_text': str
            }
        """
        if not text or not isinstance(text, str):
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'processed_text': ''
            }

        # Nếu model chưa load, trả về neutral
        if self._model is None or self._preprocessor is None:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'processed_text': text
            }

        try:
            # Tiền xử lý text
            processed_text = self._preprocessor.forward(text)

            if not processed_text.strip():
                return {
                    'sentiment': 'neutral',
                    'score': 0.0,
                    'processed_text': processed_text
                }

            # Predict
            labels, probs = self._model.predict(processed_text, k=2)

            # Parse result
            # labels format: ('__label__positive', '__label__negative')
            primary_label = labels[0].replace('__label__', '')
            confidence = probs[0]

            # Calculate score (-1 to 1)
            if primary_label == 'positive':
                score = confidence
                sentiment = 'positive' if confidence > 0.6 else 'neutral'
            else:
                score = -confidence
                sentiment = 'negative' if confidence > 0.6 else 'neutral'

            return {
                'sentiment': sentiment,
                'score': round(score, 4),
                'processed_text': processed_text
            }

        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'processed_text': text
            }

    def is_ready(self) -> bool:
        """Kiểm tra model đã sẵn sàng chưa"""
        return self._model is not None and self._preprocessor is not None
