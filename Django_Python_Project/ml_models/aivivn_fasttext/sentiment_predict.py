import fasttext
from Django_Python_Project.ml_models.aivivn_fasttext.config import MODEL_DIR
from Django_Python_Project.ml_models.aivivn_fasttext.preprocess import PreprocessText

MODEL_PATH = MODEL_DIR / "fasttext_sentiment.bin"


class SentimentPredictor:
    def __init__(self, model_path=None):
        """Load model và preprocessing"""
        # Cho phép truyền path tùy chỉnh
        path = model_path if model_path else MODEL_PATH
        
        if not path.exists():
            raise FileNotFoundError(
                f"Model không tồn tại: {path}\n"
                f"Hãy chạy train.py trước để tạo model!"
            )
        
        self.model = fasttext.load_model(str(path))
        self.preprocess = PreprocessText()
        print(f"✓ Đã load model từ: {path}")
    
    def predict(self, text: str):
        """
        Dự đoán sentiment cho 1 câu
        
        Returns:
            dict: {'label': '0' hoặc '1', 'confidence': 0.95}
        """
        # Kiểm tra text rỗng
        if not text or not text.strip():
            return {
                "label": "unknown",
                "confidence": 0.0
            }
        
        # Tiền xử lý text giống như khi train
        processed_text = self.preprocess.forward(text)
        
        # Dự đoán
        labels, probs = self.model.predict(processed_text, k=1)
        
        # Kiểm tra kết quả
        if not labels or not probs:
            return {
                "label": "unknown",
                "confidence": 0.0
            }
        
        # Format kết quả
        label = labels[0].replace("__label__", "")
        confidence = float(probs[0])
        
        return {
            "label": label,
            "confidence": confidence
        }
    
    def predict_batch(self, texts: list):
        """
        Dự đoán sentiment cho nhiều câu
        
        Returns:
            list: [{'text': '...', 'label': '0', 'confidence': 0.95}, ...]
        """
        results = []
        for text in texts:
            pred = self.predict(text)
            results.append({
                "text": text,
                "label": pred["label"],
                "confidence": pred["confidence"]
            })
        return results


# Ví dụ sử dụng
if __name__ == "__main__":
    predictor = SentimentPredictor()
    
    # Test với 1 câu
    text = "Sản phẩm rất tốt, tôi rất hài lòng!"
    result = predictor.predict(text)
    print(f"\nText: {text}")
    print(f"Label: {result['label']} (confidence: {result['confidence']:.4f})")
    
    # Test với nhiều câu
    texts = [
        "Sản phẩm rất tốt, tôi rất hài lòng!",
        "Chất lượng tệ, không đáng tiền",
        "Bình thường, không có gì đặc biệt"
    ]
    
    print("\n" + "="*50)
    print("Dự đoán nhiều câu:")
    print("="*50)
    results = predictor.predict_batch(texts)
    for r in results:
        print(f"Text: {r['text']}")
        print(f"→ Label: {r['label']} ({r['confidence']:.4f})\n")