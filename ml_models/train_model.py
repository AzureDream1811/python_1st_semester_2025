"""
Training Sentiment Analysis Model
Sử dụng fastText với dataset AIViVN 2019
"""

import os
import fasttext

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))


def train_model(
    train_file='train_final.txt',
    model_name='sentiment_model',
    lr=0.1,
    epoch=25,
    wordNgrams=2,
    dim=100,
    loss='softmax',
    verbose=2
):
    """
    Train fastText supervised model
    
    Parameters:
    -----------
    train_file : str
        Tên file training data (format fastText)
    model_name : str
        Tên model output
    lr : float
        Learning rate
    epoch : int
        Số epoch training
    wordNgrams : int
        Sử dụng n-grams (1 = unigram, 2 = bigram, ...)
    dim : int
        Dimension của word vectors
    loss : str
        Loss function ('softmax', 'ova', 'ns')
    verbose : int
        Mức độ chi tiết log (0, 1, 2)
    
    Returns:
    --------
    fasttext model object
    """
    train_path = os.path.join(DATA_DIR, train_file)
    model_path = os.path.join(MODEL_DIR, f'{model_name}.bin')
    
    # Kiểm tra file training
    if not os.path.exists(train_path):
        print(f"Training file not found: {train_path}")
        print("Please run preprocess.py first!")
        return None
    
    print("=" * 50)
    print("TRAINING SENTIMENT MODEL")
    print("=" * 50)
    print(f"\nTraining file: {train_path}")
    print(f"Model output: {model_path}")
    print(f"\nHyperparameters:")
    print(f"  - Learning rate: {lr}")
    print(f"  - Epochs: {epoch}")
    print(f"  - Word n-grams: {wordNgrams}")
    print(f"  - Dimension: {dim}")
    print(f"  - Loss: {loss}")
    
    print("\nTraining...")
    
    # Train model
    model = fasttext.train_supervised(
        input=train_path,
        lr=lr,
        epoch=epoch,
        wordNgrams=wordNgrams,
        dim=dim,
        loss=loss,
        verbose=verbose
    )
    
    # Save model
    model.save_model(model_path)
    print(f"\nModel saved to: {model_path}")
    
    return model


def evaluate_model(model, test_file='test_final.txt'):
    """
    Đánh giá model trên test set
    """
    test_path = os.path.join(DATA_DIR, test_file)
    
    if not os.path.exists(test_path):
        print(f"Test file not found: {test_path}")
        return None
    
    print("\n" + "=" * 50)
    print("EVALUATING MODEL")
    print("=" * 50)
    
    # Test model
    result = model.test(test_path)
    
    print(f"\nTest samples: {result[0]}")
    print(f"Precision: {result[1]:.4f}")
    print(f"Recall: {result[2]:.4f}")
    
    # F1 Score
    if result[1] + result[2] > 0:
        f1 = 2 * result[1] * result[2] / (result[1] + result[2])
        print(f"F1 Score: {f1:.4f}")
    
    return result


def test_predictions(model):
    """
    Test model với một số ví dụ
    """
    print("\n" + "=" * 50)
    print("TESTING PREDICTIONS")
    print("=" * 50)
    
    test_texts = [
        "Sản phẩm rất tốt, tôi rất hài lòng",
        "Hàng đẹp, đúng mô tả, giao hàng nhanh",
        "Sản phẩm tệ, không như mô tả, thất vọng",
        "Hàng giả, chất lượng kém, lừa đảo",
        "Sản phẩm tạm được, không có gì đặc biệt",
        "Giao hàng nhanh, đóng gói cẩn thận",
        "Chất lượng không như mong đợi",
        "Tuyệt vời, sẽ mua lần sau",
        "Hơi đắt nhưng chất lượng tốt",
        "Không đáng tiền, khuyên không nên mua"
    ]
    
    print("\nTest predictions:\n")
    for text in test_texts:
        prediction = model.predict(text)
        label = prediction[0][0].replace('__label__', '')
        confidence = prediction[1][0]
        
        emoji = "✅" if label == "positive" else "❌"
        print(f"{emoji} [{label:8s}] ({confidence:.3f}) : {text}")


def hyperparameter_search(train_file='train_final.txt', test_file='test_final.txt'):
    """
    Tìm kiếm hyperparameters tốt nhất
    """
    train_path = os.path.join(DATA_DIR, train_file)
    test_path = os.path.join(DATA_DIR, test_file)
    
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        print("Training/Test files not found!")
        return None
    
    print("\n" + "=" * 50)
    print("HYPERPARAMETER SEARCH")
    print("=" * 50)
    
    best_f1 = 0
    best_params = {}
    
    # Grid search
    lr_values = [0.05, 0.1, 0.2]
    epoch_values = [15, 25, 50]
    ngram_values = [1, 2, 3]
    dim_values = [50, 100, 200]
    
    total_combinations = len(lr_values) * len(epoch_values) * len(ngram_values) * len(dim_values)
    current = 0
    
    for lr in lr_values:
        for epoch in epoch_values:
            for ngram in ngram_values:
                for dim in dim_values:
                    current += 1
                    print(f"\n[{current}/{total_combinations}] Testing: lr={lr}, epoch={epoch}, ngram={ngram}, dim={dim}")
                    
                    model = fasttext.train_supervised(
                        input=train_path,
                        lr=lr,
                        epoch=epoch,
                        wordNgrams=ngram,
                        dim=dim,
                        loss='softmax',
                        verbose=0
                    )
                    
                    result = model.test(test_path)
                    precision = result[1]
                    recall = result[2]
                    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
                    
                    print(f"  -> P={precision:.4f}, R={recall:.4f}, F1={f1:.4f}")
                    
                    if f1 > best_f1:
                        best_f1 = f1
                        best_params = {
                            'lr': lr,
                            'epoch': epoch,
                            'wordNgrams': ngram,
                            'dim': dim
                        }
    
    print("\n" + "=" * 50)
    print("BEST HYPERPARAMETERS")
    print("=" * 50)
    print(f"Best F1 Score: {best_f1:.4f}")
    print(f"Best Parameters: {best_params}")
    
    return best_params


def load_model(model_name='sentiment_model'):
    """
    Load trained model
    """
    model_path = os.path.join(MODEL_DIR, f'{model_name}.bin')
    
    if not os.path.exists(model_path):
        print(f"Model not found: {model_path}")
        return None
    
    return fasttext.load_model(model_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'search':
        # Hyperparameter search
        best_params = hyperparameter_search()
        if best_params:
            print("\nTraining with best params...")
            model = train_model(**best_params)
    else:
        # Normal training
        model = train_model()
        
        if model:
            # Evaluate
            evaluate_model(model)
            
            # Test predictions
            test_predictions(model)
            
            print("\n" + "=" * 50)
            print("TRAINING COMPLETED!")
            print("=" * 50)
