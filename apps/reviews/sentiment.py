"""
Sentiment Analyzer sử dụng fastText và Underthesea
Phân tích cảm xúc review sản phẩm tiếng Việt
Tạm thời bị lỗi khi deploy đang suy tính dùng cái khác
"""

import os
import re
from django.conf import settings

try:
    import fasttext
    # Tắt warning của fastText
    fasttext.FastText.eprint = lambda x: None
    FASTTEXT_AVAILABLE = True
except ImportError:
    fasttext = None
    FASTTEXT_AVAILABLE = False
    print("Warning: fasttext not installed.")


class SentimentAnalyzer:
    """
    Class phân tích sentiment cho review tiếng Việt
    Sử dụng fastText model được train từ dataset AIViVN 2019
    """
    
    _instance = None
    _model = None
    
    def __new__(cls):
        """Singleton pattern để chỉ load model một lần"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self.load_model()
    
    def load_model(self):
        """Load fastText model"""
        if not FASTTEXT_AVAILABLE:
            print("fasttext not available. Using rule-based sentiment analysis.")
            self._model = None
            return

        model_path = getattr(settings, 'SENTIMENT_MODEL_PATH', None)
        
        if model_path and os.path.exists(model_path):
            try:
                self._model = fasttext.load_model(str(model_path))
                print(f"Loaded sentiment model from {model_path}")
            except Exception as e:
                print(f"Error loading model: {e}")
                self._model = None
        else:
            print(f"Model not found at {model_path}. Using rule-based fallback.")
            self._model = None
    
    def preprocess_text(self, text):
        """
        Tiền xử lý text tiếng Việt
        - Lowercase
        - Xóa HTML tags
        - Xóa URLs
        - Xóa ký tự đặc biệt
        - Word tokenize với Underthesea
        """
        if not text:
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Xóa HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Xóa URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Xóa email
        text = re.sub(r'\S+@\S+', '', text)
        
        # Xóa số điện thoại
        text = re.sub(r'\b\d{10,11}\b', '', text)
        
        # Xóa ký tự đặc biệt, giữ lại tiếng Việt và số
        text = re.sub(r'[^\w\sàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]', ' ', text)
        
        # Xóa khoảng trắng thừa
        text = ' '.join(text.split())
        
        # Word tokenize với Underthesea
        try:
            from underthesea import word_tokenize
            text = word_tokenize(text, format="text")
        except ImportError:
            pass  # Nếu không có underthesea thì giữ nguyên
        
        return text.strip()
    
    def analyze(self, text):
        """
        Phân tích sentiment của text
        
        Args:
            text: Nội dung review cần phân tích
            
        Returns:
            dict: {
                'sentiment': 'positive' | 'negative' | 'neutral',
                'score': float (-1 đến 1),
                'confidence': float (0 đến 1),
                'processed_text': str
            }
        """
        processed_text = self.preprocess_text(text)
        
        if not processed_text:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'processed_text': ''
            }
        
        if self._model:
            return self._predict_with_model(processed_text)
        else:
            return self._predict_rule_based(processed_text)
    
    def _predict_with_model(self, text):
        """Dự đoán với fastText model"""
        try:
            prediction = self._model.predict(text)
            label = prediction[0][0]  # __label__positive hoặc __label__negative
            confidence = prediction[1][0]
            
            # Xác định sentiment từ label
            if '__label__positive' in label or '__label__1' in label:
                sentiment = 'positive'
                score = confidence
            elif '__label__negative' in label or '__label__0' in label:
                sentiment = 'negative'
                score = -confidence
            else:
                sentiment = 'neutral'
                score = 0.0
            
            # Điều chỉnh neutral threshold
            if abs(score) < 0.3:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'score': round(score, 4),
                'confidence': round(confidence, 4),
                'processed_text': text
            }
        except Exception as e:
            print(f"Model prediction error: {e}")
            return self._predict_rule_based(text)
    
    def _predict_rule_based(self, text):
        """
        Fallback: Dự đoán dựa trên từ khóa
        Sử dụng khi model không khả dụng
        """
        # Từ khóa tích cực
        positive_words = [
            'tốt', 'tuyệt vời', 'xuất sắc', 'hài lòng', 'chất lượng',
            'đẹp', 'nhanh', 'ổn', 'ok', 'good', 'nice', 'great',
            'thích', 'yêu', 'tuyệt', 'hoàn hảo', 'đáng tiền',
            'giá tốt', 'giao nhanh', 'đóng gói cẩn thận', 'nhiệt tình',
            'uy tín', 'chính hãng', 'recommend', 'khuyên dùng',
            'rất tốt', 'rất đẹp', 'rất hài lòng', 'xịn', 'chất',
            'đỉnh', 'max', 'chuẩn', 'ngon', 'mượt', 'nhanh nhạy'
        ]
        
        # Từ khóa tiêu cực
        negative_words = [
            'tệ', 'kém', 'xấu', 'chậm', 'dở', 'hỏng', 'lỗi',
            'thất vọng', 'không hài lòng', 'không tốt', 'không đáng',
            'gian lận', 'lừa đảo', 'fake', 'giả', 'nhái',
            'giao chậm', 'đóng gói cẩu thả', 'hư', 'vỡ', 'móp',
            'không như mô tả', 'khác mô tả', 'không giống hình',
            'bad', 'poor', 'terrible', 'worst', 'không ổn',
            'dở', 'tệ hại', 'quá tệ', 'rất tệ', 'thất vọng',
            'không mua', 'không nên mua', 'cảnh báo', 'không recommend'
        ]
        
        # Đếm từ khóa
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.5,
                'processed_text': text
            }
        
        # Tính score
        score = (positive_count - negative_count) / total
        
        # Xác định sentiment
        if score > 0.2:
            sentiment = 'positive'
        elif score < -0.2:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': round(score, 4),
            'confidence': round(min(total / 5, 1.0), 4),  # Confidence dựa trên số từ khóa
            'processed_text': text
        }
    
    def batch_analyze(self, texts):
        """
        Phân tích nhiều texts cùng lúc
        
        Args:
            texts: List các text cần phân tích
            
        Returns:
            List các kết quả phân tích
        """
        return [self.analyze(text) for text in texts]


# Singleton instance
_analyzer = None


def get_analyzer():
    """Lấy instance của SentimentAnalyzer"""
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    return _analyzer


def analyze_sentiment(text):
    """
    Hàm tiện ích để phân tích sentiment
    
    Args:
        text: Nội dung cần phân tích
        
    Returns:
        dict: Kết quả phân tích sentiment
    """
    analyzer = get_analyzer()
    return analyzer.analyze(text)
