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

    Parameters
    ----------
    model : fasttext.FastText
        The trained fastText model to evaluate.
    valid_path : Path
        The path to the validation data file.
    dataset_name : str, optional
        Name of the dataset being evaluated (for display).

    Returns
    -------
    N : int
        The number of test examples.
    p1 : float
        The precision at 1.
    r1 : float
        The recall at 1.
    """
    N, p1, r1 = model.test(str(valid_path))
    f1 = 2 * p1 * r1 / (p1 + r1) if (p1 + r1) > 0 else 0
    print(f"{dataset_name}: P@1={p1:.4f}, R@1={r1:.4f}, F1={f1:.4f}")
    return N, p1, r1


def main():
    print("Training fastText model...")
    print(f"Train: {TRAIN_FILE.name}, Val: {VAL_FILE.name}, Test: {TEST_FILE.name}")
    print(f"Epochs: {EPOCHS}, LR: {LR}, Dim: {DIM}, Word n-grams: {WORD_NGRAMS}\n")

    # Kiểm tra files
    if not TRAIN_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy train file: {TRAIN_FILE}")
    if not VAL_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy validation file: {VAL_FILE}")
    if not TEST_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy test file: {TEST_FILE}")

    # Train model
    print("Training...\n")
    model = train_fasttext(TRAIN_FILE)

    # Evaluate
    print("\nResults:")
    evaluate(model, VAL_FILE, "Validation")
    evaluate(model, TEST_FILE, "Test")

    print(f"\nModel saved: {MODEL_PATH}")


if __name__ == "__main__":
    main()