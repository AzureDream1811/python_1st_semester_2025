import pandas as pd
from underthesea import word_tokenize, text_normalize
import emoji
import re
import fasttext
import os

PROJECT_DIR = os.path.dirname(__file__)

class PreProcessing(object):

    _replacements = {
        "laems": "lắm",
        "k dk": "không được",
        "ko": "không",
        "ko tl": "không trả lời",
        "hok": "không",
        "hàg": "hàng",
        "kp": "không phải",
        "khong xl": "không xin lỗi",
        "khong": "không",
        "k": "không",
        "thik": "thích",
        "xog": "xong",
        "e bé": "em bé",
        "tks": "cảm ơn",
        "thanks": "cảm ơn",
        "sp": "sản phẩm",
        "sx": "sản xuất",
        "meosddc": "méo được",
        "cg": "cũng",
        "cgiac": "cảm giác",
        "siu": "siêu",
        "dt": "điện thoại",
        "đc": "được",
        "trc": "trước",
        "lhe": "liên hệ",
        "nt": "nhắn tin",
        "ntn": "như thế nào",
        "thấy ntn": "thấy như thế này",
        "k bt ntn": "không biết như thế nào",
        "shopkhá": "cửa hàng khá",
        "phẩmkémvề ": "phẩm kém về ",
        "tl": "trả lời",
        "lắmmàu": "lắm màu",
        "êmda": "êm da",
        "thj": "thì"
    }

    
    _remove_str = ["♡ ♡ ♡","❤","\=\)\)\)", "\=\)\)", "\=\)","\:\)\)\)", "\:\)\)", "\:\)"]

    def _get_replacements_pattern(self):
        replacements = {}

        for k,v in PreProcessing._replacements.items():
            if k != "k bt ntn":
                replacements[f" {k} "] = f" {v} " 
            else:
                replacements[f"{k} "] = f"{v} " 


        return re.compile("|".join(replacements.keys())), replacements, re.compile("|".join(PreProcessing._remove_str))
        
    def __init__(self):
        self._replacements_pattern, self.replacements, self._remove_pattern = self._get_replacements_pattern()


    def forward(self, text:str):
        # 1. lower all string
        text = text.lower()

        # 2. normalize
        text = text_normalize(text)

        # 3. remove emojies
        text = emoji.replace_emoji(text, replace='')

        # 4. remove words
        text = self._remove_pattern.sub('', text)

        # 5. replace words
        text = self._replacements_pattern.sub(lambda match: self.replacements[match.group()], text)

        # 6. remove any ',' left after cleaning words
        text = re.sub(r"\,\s",'',text)

        # 7. tokenize via underthesea
        text = word_tokenize(text, format="text")

        return text


class FastTextTrainingPipeline:
    def __init__(
        self,
        output_dir: str,
        text_col: str = "comment",
        label_col: str = "label",
    ):
        
        self.output_dir = output_dir
        self.text_col = text_col
        self.label_col = label_col
        os.makedirs(os.path.join(PROJECT_DIR,output_dir), exist_ok=True) # Tạo thư mục đích
        
        self._pre_processing = PreProcessing()

    
    def preprocess(self, df: pd.DataFrame):
        
        df[self.text_col] = (
            df[self.text_col].astype(str).map(self._pre_processing.forward)
        )
        return df

    
    def build_fasttext_lines(self, df: pd.DataFrame):

        def to_fasttext_format(label, text) -> str:
            """Định dạng 1 mẫu cho fastText: '__label__<label> <text>'."""
            return f"__label__{label} {text}"

        
        df["ft_line"] = [
            to_fasttext_format(label, text)
            for label, text in zip(df[self.label_col], df[self.text_col])
        ]
        return df

    
    def train_model(
        self,
        train_path: str,
        lr=0.3,
        epoch=15,
        wordNgrams=2,
        dim=100,
        loss="hs",
        minn=2,
        maxn=5,
    ):
        
        return fasttext.train_supervised(
            input=train_path,
            lr=lr,
            epoch=epoch,
            wordNgrams=wordNgrams,
            dim=dim,
            loss=loss,
            minn=minn,
            maxn=maxn,
        )
    
    def evaluate(self, valid_path: str, model):
        """
        Đánh giá trên tập validation:
        - model.test(path) trả về (N, precision@1, recall@1)
          + N: số mẫu
          + precision@1: tỉ lệ dự đoán đúng trên tổng số dự đoán (top-1)
          + recall@1: tỉ lệ bắt trúng nhãn đúng trên tổng số mẫu đúng (top-1)
        """
        
        # model.test() returns (total_samples, precision@1, recall@1)
        N, p1, r1 = model.test(valid_path)
        print(f"   N={N}  Precision@1={p1:.4f}  Recall@1={r1:.4f}")
        return N, p1, r1


    def run_full_pipeline(self, train_csv_path: str, test_csv_path: str):
        train_df = pd.read_csv(os.path.join(PROJECT_DIR,train_csv_path))
        test_df = pd.read_csv(os.path.join(PROJECT_DIR,test_csv_path))
        
        processed_train_df = self.preprocess(train_df)
        processed_test_df = self.preprocess(test_df)

        processed_train_df = self.build_fasttext_lines(processed_train_df)
        processed_test_df = self.build_fasttext_lines(processed_test_df)

        
        train_path = os.path.join(PROJECT_DIR,self.output_dir, "train.txt")
        test_path = os.path.join(PROJECT_DIR,self.output_dir, "test.txt")
        processed_train_df['ft_line'].to_csv(train_path, index=False, header=False)
        processed_test_df['ft_line'].to_csv(test_path, index=False, header=False)


        trained_model = self.train_model(train_path)
        self.evaluate(test_path, trained_model)
        
        trained_model.save_model(os.path.join(PROJECT_DIR, self.output_dir, "fasttext_sentiment.bin"))
        


# ---------- Run example ----------
if __name__ == "__main__":
    pipeline = FastTextTrainingPipeline(
        output_dir="output",
    )
    pipeline.run_full_pipeline(
        train_csv_path="dataset/train.csv",
        test_csv_path="dataset/test.csv",
    )

