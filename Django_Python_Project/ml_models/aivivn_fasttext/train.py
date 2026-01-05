from pathlib import Path
import fasttext

from Django_Python_Project.ml_models.aivivn_fasttext.config import (
    TRAIN_FILE,
    VAL_FILE,
    TEST_FILE,
    MODEL_DIR,
    EPOCHS,
    LR,
    DIM,
    WORD_NGRAMS,
)

MODEL_PATH = MODEL_DIR / "fasttext_sentiment.bin"


def train_fasttext(
    input_path: Path,
    epochs: int = EPOCHS,
    lr: float = LR,
    dim: int = DIM,
    word_ngrams: int = WORD_NGRAMS,
    loss: str = "softmax",
    minn: int = 2,
    maxn: int = 5,
):
    """
    Train a fastText supervised model.

    Parameters
    ----------
    input_path : Path
        The path to the training data file.
    epochs : int, optional
        The number of epochs to train the model. Defaults to EPOCHS.
    lr : float, optional
        The learning rate of the model. Defaults to LR.
    dim : int, optional
        The dimension of the model. Defaults to DIM.
    word_ngrams : int, optional
        The number of word n-grams to use. Defaults to WORD_NGRAMS.
    loss : str, optional
        The loss function to use. Defaults to "softmax".
    minn : int, optional
        The minimum length of a word to include in the vocab. Defaults to 2.
    maxn : int, optional
        The maximum length of a word to include in the vocab. Defaults to 5.

    Returns
    -------
    model : fasttext.FastText
        The trained fastText model.
    """
    print(f"Đang train với file: {input_path}")
    
    model = fasttext.train_supervised(
        input=str(input_path),
        lr=lr,
        epoch=epochs,
        wordNgrams=word_ngrams,
        dim=dim,
        loss=loss,
        minn=minn,
        maxn=maxn,
    )

    print(f"Đang lưu model vào: {MODEL_PATH}")
    model.save_model(str(MODEL_PATH))
    print("✓ Đã lưu model thành công!")
    
    return model


def evaluate(model, valid_path: Path, dataset_name: str = ""):
    """
    Evaluate a trained fastText supervised model on a validation set.

    Returns
    -------
    N : int
        The number of test examples.
    p1 : float
        The precision at 1.
    r1 : float
        The recall at 1.
    f1 : float
        The F1 score.
    """
    N, p1, r1 = model.test(str(valid_path))
    f1 = 2 * p1 * r1 / (p1 + r1) if (p1 + r1) > 0 else 0
    print(f"{dataset_name}: P@1={p1:.4f}, R@1={r1:.4f}, F1={f1:.4f}")
    return N, p1, r1, f1


def main():
    print("Training fastText model...")
    print(f"Train: {TRAIN_FILE.name}, Val: {VAL_FILE.name}, Test: {TEST_FILE.name}")
    print(f"Epochs: {EPOCHS}, LR: {LR}, Dim: {DIM}, Word n-grams: {WORD_NGRAMS}\n")

    model = train_fasttext(TRAIN_FILE)

    print("\n" + "="*50)
    print("ĐÁNH GIÁ ĐẦY ĐỦ")
    print("="*50)
    
    _, _, _, train_f1 = evaluate(model, TRAIN_FILE, "Train")
    _, _, _, val_f1 = evaluate(model, VAL_FILE, "Validation")
    _, _, _, test_f1 = evaluate(model, TEST_FILE, "Test")
    
    gap = train_f1 - val_f1
    
    print("\n" + "="*50)
    print("PHÂN TÍCH:")
    print("="*50)
    print(f"Train-Val Gap: {gap:.4f} ({gap*100:.2f}%)")
    
    if gap > 0.15:
        print("❌ OVERFITTING nghiêm trọng!")
    elif gap > 0.10:
        print("⚠️  Có dấu hiệu overfitting")
    elif gap > 0.05:
        print("✅ Overfitting nhẹ - chấp nhận được")
    else:
        print("✅ Model cân bằng rất tốt!")
    
    if val_f1 >= 0.85:
        print("✅ Performance XUẤT SẮC!")
    elif val_f1 >= 0.80:
        print("✅ Performance TỐT!")
    elif val_f1 >= 0.75:
        print("✅ Performance CHẤP NHẬN ĐƯỢC")
    else:
        print("⚠️  Performance cần cải thiện")


if __name__ == "__main__":
    main()