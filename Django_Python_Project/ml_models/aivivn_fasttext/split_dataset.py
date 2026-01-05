import pandas as pd
from sklearn.model_selection import train_test_split
from Django_Python_Project.ml_models.aivivn_fasttext.config import DATASET_DIR

# Đọc data
df = pd.read_csv(DATASET_DIR / "train.csv")

print(f"Tổng số mẫu trong train.csv: {len(df)}")
print(f"Tên các cột: {df.columns.tolist()}")  # THÊM: Xem tên cột thực tế
print("\nMẫu dữ liệu đầu tiên:")
print(df.head())  # THÊM: Xem dữ liệu mẫu

# Tìm tên cột label (có thể là 'label', 'sentiment', 'target', v.v.)
# SỬA tên cột này sau khi xem output trên
label_col = 'label'  # Hoặc 'sentiment', 'target', tùy dataset

# Chia train.csv thành 90% train và 10% val
train_df, val_df = train_test_split(
    df, 
    test_size=0.1,
    random_state=42, 
    stratify=df[label_col]  # Sử dụng tên cột đúng
)

# Lưu ra 2 file mới
train_df.to_csv(DATASET_DIR / "train_split.csv", index=False)
val_df.to_csv(DATASET_DIR / "val.csv", index=False)

print(f"\nTrain: {len(train_df)} mẫu ({len(train_df)/len(df)*100:.1f}%)")
print(f"Val: {len(val_df)} mẫu ({len(val_df)/len(df)*100:.1f}%)")
print("\nĐã tạo: train_split.csv, val.csv")
print("Giữ nguyên: test.csv (từ AIVIVN)")