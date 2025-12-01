"""
Tiền xử lý dữ liệu cho Sentiment Analysis
Dataset: AIViVN 2019 (Kaggle)
"""

import os
import re
import pandas as pd
from underthesea import word_tokenize

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')


def clean_text(text):
    """
    Làm sạch text tiếng Việt
    """
    if pd.isna(text):
        return ""
    
    text = str(text)
    
    # Lowercase
    text = text.lower()
    
    # Xóa HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Xóa URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Xóa emails
    text = re.sub(r'\S+@\S+', '', text)
    
    # Xóa số điện thoại
    text = re.sub(r'\b\d{10,11}\b', '', text)
    
    # Xóa ký tự đặc biệt, giữ lại tiếng Việt
    text = re.sub(r'[^\w\sàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]', ' ', text)
    
    # Xóa khoảng trắng thừa
    text = ' '.join(text.split())
    
    return text.strip()


def tokenize_text(text):
    """
    Tokenize text tiếng Việt với Underthesea
    """
    if not text:
        return ""
    
    try:
        return word_tokenize(text, format="text")
    except Exception as e:
        print(f"Tokenization error: {e}")
        return text


def preprocess_dataset(input_file='train.csv', output_file='train_processed.csv'):
    """
    Tiền xử lý toàn bộ dataset
    """
    input_path = os.path.join(RAW_DATA_DIR, input_file)
    output_path = os.path.join(PROCESSED_DATA_DIR, output_file)
    
    # Tạo thư mục nếu chưa có
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
    print(f"Loading data from {input_path}...")
    
    # Đọc dataset
    # Dataset AIViVN có các columns: id, comment, label (0 hoặc 1)
    try:
        df = pd.read_csv(input_path, encoding='utf-8')
    except FileNotFoundError:
        print(f"File not found: {input_path}")
        print("Please download the dataset from Kaggle:")
        print("https://www.kaggle.com/datasets/mcocoz/aivivn-2019")
        return None
    
    print(f"Loaded {len(df)} records")
    
    # Xác định column names
    # Dataset có thể có các tên khác nhau
    text_col = None
    label_col = None
    
    for col in df.columns:
        if col.lower() in ['comment', 'text', 'review', 'content']:
            text_col = col
        if col.lower() in ['label', 'sentiment', 'rating']:
            label_col = col
    
    if not text_col:
        # Nếu không tìm thấy, dùng column thứ 2
        text_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
    
    if not label_col and len(df.columns) > 2:
        label_col = df.columns[2]
    
    print(f"Using text column: {text_col}")
    print(f"Using label column: {label_col}")
    
    # Làm sạch text
    print("Cleaning text...")
    df['cleaned_text'] = df[text_col].apply(clean_text)
    
    # Tokenize
    print("Tokenizing text...")
    df['processed_text'] = df['cleaned_text'].apply(tokenize_text)
    
    # Xử lý label
    if label_col:
        df['sentiment'] = df[label_col]
    else:
        df['sentiment'] = 1  # Default positive
    
    # Xóa các rows trống
    df = df[df['processed_text'].str.len() > 0]
    
    print(f"After cleaning: {len(df)} records")
    
    # Lưu file
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Saved processed data to {output_path}")
    
    # Thống kê
    print("\n=== Statistics ===")
    print(f"Total records: {len(df)}")
    if label_col:
        print(f"Positive (1): {(df['sentiment'] == 1).sum()}")
        print(f"Negative (0): {(df['sentiment'] == 0).sum()}")
    
    return df


def prepare_fasttext_format(input_file='train_processed.csv', output_file='train.txt'):
    """
    Chuyển đổi sang format fastText
    Format: __label__<class> <text>
    """
    input_path = os.path.join(PROCESSED_DATA_DIR, input_file)
    output_path = os.path.join(PROCESSED_DATA_DIR, output_file)
    
    print(f"Loading processed data from {input_path}...")
    
    try:
        df = pd.read_csv(input_path, encoding='utf-8')
    except FileNotFoundError:
        print(f"File not found: {input_path}")
        print("Please run preprocess_dataset() first")
        return None
    
    print(f"Preparing fastText format...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            text = row['processed_text']
            if pd.isna(text) or not text.strip():
                continue
            
            # Label: 1 = positive, 0 = negative
            label = '__label__positive' if row['sentiment'] == 1 else '__label__negative'
            
            # Viết dòng: __label__xxx text...
            f.write(f"{label} {text}\n")
    
    print(f"Saved fastText format to {output_path}")
    
    # Đếm số dòng
    with open(output_path, 'r', encoding='utf-8') as f:
        line_count = sum(1 for _ in f)
    print(f"Total lines: {line_count}")
    
    return output_path


def split_train_test(input_file='train.txt', test_ratio=0.1):
    """
    Chia train/test set
    """
    import random
    
    input_path = os.path.join(PROCESSED_DATA_DIR, input_file)
    train_path = os.path.join(PROCESSED_DATA_DIR, 'train_final.txt')
    test_path = os.path.join(PROCESSED_DATA_DIR, 'test_final.txt')
    
    print(f"Splitting dataset...")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    random.shuffle(lines)
    
    split_idx = int(len(lines) * (1 - test_ratio))
    train_lines = lines[:split_idx]
    test_lines = lines[split_idx:]
    
    with open(train_path, 'w', encoding='utf-8') as f:
        f.writelines(train_lines)
    
    with open(test_path, 'w', encoding='utf-8') as f:
        f.writelines(test_lines)
    
    print(f"Train set: {len(train_lines)} samples -> {train_path}")
    print(f"Test set: {len(test_lines)} samples -> {test_path}")
    
    return train_path, test_path


if __name__ == "__main__":
    print("=" * 50)
    print("SENTIMENT ANALYSIS - DATA PREPROCESSING")
    print("=" * 50)
    
    # Bước 1: Tiền xử lý
    print("\n[Step 1] Preprocessing dataset...")
    df = preprocess_dataset()
    
    if df is not None:
        # Bước 2: Chuyển sang format fastText
        print("\n[Step 2] Converting to fastText format...")
        prepare_fasttext_format()
        
        # Bước 3: Chia train/test
        print("\n[Step 3] Splitting train/test...")
        split_train_test()
        
        print("\n" + "=" * 50)
        print("PREPROCESSING COMPLETED!")
        print("=" * 50)
