# -*- coding: utf-8 -*-
"""
FastText Vietnamese Classification (OOP version)
This class version keeps the same 9-step pipeline, but wrapped into methods.
"""

import os
import re
import pandas as pd
from sklearn.model_selection import train_test_split  # chia dữ liệu
import fasttext

# Optional Vietnamese tokenizer
try:
    from underthesea import word_tokenize  # Hàm tách từ tiếng Việt


    def tokenize_vi(s):  # type: ignore
        """Biến 'Hà Nội đẹp' -> 'Hà_Nội đẹp' (format="text" ghép token bằng dấu '_')."""
        return word_tokenize(s, format="text")
except Exception:

    def tokenize_vi(s):
        return s  # fallback: no tokenization


# ---------- Helper functions ----------
def clean_vi(text: str) -> str:
    """Đưa về chữ thường + gộp khoảng trắng."""
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def to_fasttext_format(label, text) -> str:
    """Định dạng 1 mẫu cho fastText: '__label__<label> <text>'."""
    return f"__label__{label} {text}"


# ---------- OOP Class ----------
class FastTextPipeline:
    def __init__(
            self,
            input_csv: str,
            output_dir: str,
            text_col: str = "comment",
            label_col: str = "label",
    ):
        """
        __init__ chạy khi KHỞI TẠO OBJECT.
        - Gán cấu hình vào self (state nội bộ) để các method khác sử dụng.
        - Tạo sẵn thư mục output (nếu chưa có).
        - Khởi tạo self.df và self.model = None (vì chưa load/train tại thời điểm này).

        Sau khi __init__:
        - self.input_csv: đường dẫn file CSV nguồn
        - self.output_dir: nơi lưu train.txt / valid.txt / model.bin
        - self.text_col / self.label_col: tên cột trong CSV
        - self.df: sẽ là pandas.DataFrame sau khi load_data()
        - self.model: sẽ là fastText model sau khi train_model()
        """
        self.input_csv = input_csv
        self.output_dir = output_dir
        self.text_col = text_col
        self.label_col = label_col
        os.makedirs(output_dir, exist_ok=True)  # Tạo thư mục đích

        # STATE nội bộ (các thuộc tính này "sinh ra" từ init):
        self.df = None  # sẽ chứa DataFrame sau load_data()
        self.model = None  # sẽ chứa mô hình fastText sau train_model()

    # [1] Load CSV
    def load_data(self):
        """
        Đọc CSV vào DataFrame và kiểm tra cột bắt buộc.

        SAU HÀM NÀY:
        - self.df != None (DataFrame sẵn sàng cho bước kế)
        - return self để có thể chain: self.load_data().preprocess()...
        """
        print("[1] Loading dataset...")
        df = pd.read_csv(self.input_csv)

        # Kiểm tra tên cột xem dataset có đúng kỳ vọng không
        if self.text_col not in df.columns or self.label_col not in df.columns:
            raise ValueError(
                f"CSV must contain '{self.text_col}' and '{self.label_col}' columns."
            )
        self.df = df  # Lúc này self.df "xuất hiện" vì gán ngay tại đây
        print("   → Loaded", len(df), "rows")
        return self

    # [2] Clean & tokenize
    def preprocess(self):
        """
        Tiền xử lý văn bản:
        - convert to str -> clean_vi -> tokenize_vi
        - clean_vi: lower + gộp khoảng trắng
        - tokenize_vi: dùng underthesea nếu có (giữ 'Hà_Nội'); nếu không thì trả nguyên
        """
        assert self.df is not None
        print("[2] Cleaning + tokenizing text...")
        self.df[self.text_col] = (
            self.df[self.text_col].astype(str).map(clean_vi).map(tokenize_vi)
        # .map(func) áp dụng hàm cho MỖI PHẦN TỬ của Series; chain nhiều .map để tạo pipeline nhỏ
        )
        return self

    # [3] Convert to fastText format
    def build_fasttext_lines(self):
        """
        Tạo cột 'ft_line' dạng: '__label__<label> <text>' để fastText đọc được.
        """
        assert self.df is not None
        print("[3] Converting to fastText format...")

        # zip(...) duyệt song song 2 cột label/text để ghép thành từng dòng fastText
        self.df["ft_line"] = [
            to_fasttext_format(label, text)
            for label, text in zip(self.df[self.label_col], self.df[self.text_col])
        ]
        return self

    # [4] Split into train/valid
    def split_data(self, test_size=0.2, random_state=42):
        """
        Chia dữ liệu 80/20 (mặc định) và LƯU thành 2 file .txt để fastText dùng.
        - stratify=self.df[self.label_col]: giữ tỉ lệ nhãn như ban đầu ở cả 2 tập.
        - Trả về (train_path, valid_path) để các bước sau dùng tiếp.
        """
        assert self.df is not None
        print(
            f"[4] Splitting train/validation ({int((1 - test_size) * 100)}/{int(test_size * 100)})..."
        )

        # train_test_split: hàm sklearn để chia dữ liệu; ở đây ta chia Series "ft_line"
        train_lines, valid_lines = train_test_split(
            self.df["ft_line"],
            test_size=test_size,
            random_state=random_state,
            stratify=self.df[self.label_col],  # GIỮ phân phối nhãn cân bằng
        )
        train_path = os.path.join(self.output_dir, "train.txt")
        valid_path = os.path.join(self.output_dir, "valid.txt")

        # Ghi file .txt: mỗi dòng là 1 mẫu fastText
        pd.Series(train_lines).to_csv(train_path, index=False, header=False)
        pd.Series(valid_lines).to_csv(valid_path, index=False, header=False)
        print("   → Saved:", train_path, "and", valid_path)
        return train_path, valid_path

    # [5] Train fastText model
    def train_model(
            self,
            train_path: str,
            lr=0.3,
            epoch=10,
            wordNgrams=2,
            dim=100,
            loss="hs",
            minn=2,
            maxn=5,
    ):
        """
        Huấn luyện mô hình fastText:
        - input: đường dẫn file 'train.txt'
        - lr: learning rate (tốc độ học)
        - epoch: số lượt lặp qua dữ liệu
        - wordNgrams: (1: unigram, 2: bigram, 3: trigram) → ngữ cảnh rộng hơn
        - dim: số chiều vector ẩn
        - loss: 'hs' (hierarchical softmax), 'softmax', hoặc 'ova' (one-vs-all)
        - minn/maxn: độ dài subword (giúp xử lý từ hiếm / biến thể, rất hữu ích cho TV)

        SAU HÀM NÀY:
        - self.model trở thành 1 đối tượng fastText đã train xong
        """
        print("[5] Training fastText model...")

        # fasttext.train_supervised: gọi vào C++ core, chạy nhanh, đọc file theo dòng
        self.model = fasttext.train_supervised(
            input=train_path,
            lr=lr,
            epoch=epoch,
            wordNgrams=wordNgrams,
            dim=dim,
            loss=loss,
            minn=minn,
            maxn=maxn,
        )
        print("   → Training completed.")
        return self  # trả self để chain: self.train_model(...).evaluate(...)

    # [6] Evaluate model
    def evaluate(self, valid_path: str):
        """
        Đánh giá trên tập validation:
        - model.test(path) trả về (N, precision@1, recall@1)
          + N: số mẫu
          + precision@1: tỉ lệ dự đoán đúng trên tổng số dự đoán (top-1)
          + recall@1: tỉ lệ bắt trúng nhãn đúng trên tổng số mẫu đúng (top-1)
        """
        assert self.model is not None
        print("[6] Evaluating model...")

        # model.test() returns (total_samples, precision@1, recall@1)
        N, p1, r1 = self.model.test(valid_path)
        print(f"   N={N}  Precision@1={p1:.4f}  Recall@1={r1:.4f}")
        return N, p1, r1

    # [7] Predict one sample
    def predict(self, text: str):
        """
        Dự đoán 1 câu:
        - Chuẩn hoá + tokenize giống pipeline train (tránh mismatch)
        - model.predict(t, k=1) → (labels, probs)
          + labels: tuple chuỗi nhãn dạng '__label__<id>'
          + probs: tuple xác suất (float)
        - Trả về (label, prob) dạng thân thiện.
        """
        assert self.model is not None
        print("[7] Predicting sample...")
        cleaned = tokenize_vi(clean_vi(text))  # ĐẢM BẢO tiền xử lý y hệt lúc train
        labels, probs = self.model.predict(cleaned, k=1)  # k=1: chỉ lấy nhãn top-1

        # labels là tuple, ví dụ: ('__label__1',)
        # Loại bỏ tiền tố '__label__' để dễ đọc:
        label = labels[0].replace("__label__", "")  # type: ignore
        prob = probs[0]
        print(f"   → '{text}'  →  label={label}, prob={prob:.3f}")
        return label, prob

    # [8] Save model
    def save_model(self, model_name="fasttext_sentiment.bin"):
        """
        Lưu mô hình ra file .bin (tất cả tham số + từ vựng + trọng số).
        Sau này chỉ cần load .bin để dự đoán, không cần train lại.
        """
        assert self.model is not None
        model_path = os.path.join(self.output_dir, model_name)
        self.model.save_model(model_path)
        print("[8] Model saved to:", model_path)
        return model_path

    # [9] Run full pipeline
    def run_full_pipeline(self):
        """
        Chạy toàn bộ pipeline theo thứ tự:
        load → preprocess → build_lines → split → train → evaluate → predict → save
        """
        print("========== FASTTEXT TRAINING PIPELINE ==========")
        train_path, valid_path = (
            self.load_data().preprocess().build_fasttext_lines().split_data()
        )
        self.train_model(train_path)
        self.evaluate(valid_path)
        self.predict("Hôm nay thời tiết thật đẹp")  # demo thử
        self.save_model()
        print("========== PIPELINE DONE ✅ ==========")


# ---------- Run example ----------
if __name__ == "__main__":
    pipeline = FastTextPipeline(
        input_csv=r"AIVIVN 2019 dataset\train.csv",
        output_dir=r"out",
    )
    pipeline.run_full_pipeline()