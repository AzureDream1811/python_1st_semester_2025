from pathlib import Path

# ml_models/aivivn_fasttext  → parent → ml_models → parent → Django_Python_Project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATASET_DIR = BASE_DIR / "datasets" / "AIVIVN 2019 dataset"

FASTESTTEXT_DATA_DIR = DATASET_DIR / "fasttext_format"
FASTESTTEXT_DATA_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_FILE = FASTESTTEXT_DATA_DIR / "train.txt"
VAL_FILE = FASTESTTEXT_DATA_DIR / "val.txt" 
TEST_FILE = FASTESTTEXT_DATA_DIR / "test.txt"

MODEL_DIR = BASE_DIR / "ml_models" / "aivivn_fasttext" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# TRAINING PARAMETERS
EPOCHS = 30
LR = 0.1
DIM = 100
WORD_NGRAMS = 2