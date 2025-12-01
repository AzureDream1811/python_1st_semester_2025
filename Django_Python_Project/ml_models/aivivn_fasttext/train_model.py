from pathlib import Path
import fasttext

from .config import TRAIN_FILE, TEST_FILE, MODEL_DIR, EPOCHS, LR, DIM, WORD_NGRAMS

MODEL_PATH = MODEL_DIR / "fasttext_sentiment.bin"


def train_fasttext(
    input_path: Path,
    epochs: int = EPOCHS,
    lr: float = LR,
    dim: int = DIM,
    word_ngrams: int = WORD_NGRAMS,
    loss: str = "hs",
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
        The loss function to use. Defaults to "hs".
    minn : int, optional
        The minimum length of a word to include in the vocab. Defaults to 2.
    maxn : int, optional
        The maximum length of a word to include in the vocab. Defaults to 5.

    Returns
    -------
    model : fasttext.FastText
        The trained fastText model.
    """
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

    model.save_model(str(MODEL_PATH))
    return model


def evaluate(model, valid_path: Path):
    """
    Evaluate a trained fastText supervised model on a validation set.

    Parameters
    ----------
    model : fasttext.FastText
        The trained fastText model to evaluate.
    valid_path : Path
        The path to the validation data file.

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
    print("Evaluating model:")
    print("-> N:", N)
    print("-> P@1:", p1)
    print("-> R@1:", r1)
    return N, p1, r1


def main():
    print("TRAIN_FILE:", TRAIN_FILE)
    print("TEST_FILE:", TEST_FILE)

    if not TRAIN_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy train file: {TRAIN_FILE}")
    if not TEST_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy test file: {TEST_FILE}")

    print("Bắt đầu train fastText...")
    model = train_fasttext(TRAIN_FILE)

    print("-> Train xong, đánh giá trên tập test...")
    evaluate(model, TEST_FILE)

    print("-> Đã lưu model tại:", MODEL_PATH)
    model.save_model(str(MODEL_PATH))


if __name__ == "__main__":
    main()
