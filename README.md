# 🛒 Đồ án Web Bán đồ điện gia dụng với Sentiment Analysis sử dụng Django và fastText

Hệ thống web bán đồ điện tử có tính năng phân tích cảm xúc (sentiment analysis) cho đánh giá sản phẩm sử dụng Django Framework và fastText.

---

## 📋 Mục lục

- [Tính năng](#-tính-năng)
- [Công nghệ sử dụng](#-công-nghệ-sử-dụng)
- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Cài đặt](#-cài-đặt)
- [Cấu hình PyCharm](#-cấu-hình-pycharm)
- [Sử dụng](#-sử-dụng)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)

---

## ✨ Tính năng

### E-commerce cơ bản:
- 👤 Đăng ký, đăng nhập, quản lý profile
- 📦 Quản lý sản phẩm (CRUD)
- 🛒 Giỏ hàng
- 💳 Đặt hàng và thanh toán
- 🔍 Tìm kiếm và lọc sản phẩm
- 📊 Quản lý đơn hàng

### Sentiment Analysis:
- 📝 Đánh giá và review sản phẩm
- 🤖 Tự động phân tích cảm xúc review (fastText)
- 📈 Thống kê sentiment theo sản phẩm
- 🎯 Hiển thị điểm sentiment (Positive/Negative)

---

## 🛠 Công nghệ sử dụng

- **Backend**: Django 4.2.7
- **Database**: MySQL
- **AI/ML**: fastText + Underthesea
- **Data Processing**: pandas, numpy
- **Frontend**: Django Templates
- **Dataset**: AIViVN 2019 (Kaggle)

---

## 💻 Yêu cầu hệ thống

- Python 3.10+
- MySQL 8.0+
- PyCharm Pro
- pip
- Git

---

## 🚀 Cài đặt

### Bước 1: Clone repository

```bash
git clone https://github.com/AzureDream1811/python_1st_semester_2025.git
cd Run-Pycharm
```

### Bước 2: Tạo Virtual Environment

**Windows (trong PyCharm Terminal):**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài đặt dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Lưu ý**:
- Nếu gặp lỗi với `mysqlclient`, cài đặt MySQL development headers:
  - **Windows**: Tải MySQL Connector/C từ [MySQL website](https://dev.mysql.com/downloads/connector/c/)

### Bước 4: Setup MySQL Database

**Khởi động MySQL và tạo database:**

```sql
-- Đăng nhập MySQL
mysql -u root -p

-- Tạo database
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Tạo user cho database (khuyến nghị)
CREATE USER 'ecommerce_user'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'ecommerce_user'@'localhost';
FLUSH PRIVILEGES;

-- Thoát MySQL
EXIT;
```

### Bước 5: Cấu hình Environment Variables

**Tạo file `.env` từ template:**

```bash
cp .env.example .env
```

**Chỉnh sửa file `.env`:**

```ini
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here-generate-a-random-string
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DATABASE_NAME=ecommerce_db
DATABASE_USER=ecommerce_user
DATABASE_PASSWORD=your_strong_password
DATABASE_HOST=localhost
DATABASE_PORT=3306

# Email Settings (optional - for production)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

**Generate SECRET_KEY:**

```python
# Chạy trong Python console
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Bước 6: Tạo Django Project và Apps

```bash
# Tạo Django project
django-admin startproject config .

# Tạo các Django apps
python manage.py startapp accounts
python manage.py startapp products
python manage.py startapp cart
python manage.py startapp orders
python manage.py startapp reviews

# Di chuyển apps vào thư mục apps/
mkdir apps
mv accounts apps/
mv products apps/
mv cart apps/
mv orders apps/
mv reviews apps/
```

### Bước 7: Cấu hình Django Settings

**Chỉnh sửa `config/settings.py`:**

```python
import os
from pathlib import Path
from decouple import config

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key from .env
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'crispy_forms',
    'crispy_bootstrap4',
    'widget_tweaks',

    # Local apps
    'apps.accounts',
    'apps.products',
    'apps.cart',
    'apps.orders',
    'apps.reviews',
]

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Custom User Model (nếu dùng)
AUTH_USER_MODEL = 'accounts.User'
```

### Bước 8: Migrations và Setup Database

```bash
# Tạo migrations
python manage.py makemigrations

# Chạy migrations
python manage.py migrate

# Tạo superuser
python manage.py createsuperuser
```

### Bước 9: Download và Setup Dataset

**Download dataset từ Kaggle:**

1. Truy cập: https://www.kaggle.com/datasets/mcocoz/aivivn-2019
2. Download dataset
3. Giải nén vào thư mục `data/raw/`

**Cấu trúc dataset:**
```
data/
├── raw/
│   ├── train.csv
│   └── test.csv
└── processed/
    └── (Để sau)
```

### Bước 10: Chạy Server

```bash
python manage.py runserver
```

Truy cập: http://127.0.0.1:8000/

---

## 🔧 Cấu hình PyCharm

### 1. Mở Project trong PyCharm

1. Mở PyCharm
2. File → Open → Chọn thư mục 

### 2. Cấu hình Python Interpreter

1. **File → Settings** (Windows)
2. **Project: Run-Pycharm → Python Interpreter**
3. Click biểu tượng ⚙️ → **Add**
4. Chọn **Existing Environment**
5. Chọn Python từ venv:
   - Windows: `venv\Scripts\python.exe`
   - Linux/Mac: `venv/bin/python`
6. Click **OK**

### 3. Enable Django Support

1. **File → Settings → Languages & Frameworks → Django**
2. Check **Enable Django Support**
3. **Django project root**: Chọn thư mục project (Run-Pycharm)
4. **Settings**: `config/settings.py`
5. **Manage script**: `manage.py`
6. Click **OK**

### 4. Cấu hình Database Tools (PyCharm Professional)

1. **View → Tool Windows → Database**
2. Click **+** → **Data Source** → **MySQL**
3. Nhập thông tin:
   - **Host**: localhost
   - **Port**: 3306
   - **Database**: ecommerce_db
   - **User**: ecommerce_user
   - **Password**: your_password
4. **Test Connection** → **OK**

### 5. Cấu hình Run/Debug Configuration

1. **Run → Edit Configurations**
2. Click **+** → **Django Server**
3. Đặt tên: "Django Server"
4. **Host**: 0.0.0.0 hoặc 127.0.0.1
5. **Port**: 8000
6. Check **No reload**
7. Click **OK**

### 6. Sử dụng Django Console

1. **Tools → Run Django Console**
2. Test:
```python
from apps.products.models import Product
Product.objects.all()
```

---

## 📖 Sử dụng

### Chạy Development Server

**Trong PyCharm:**
- Click nút ▶️ (Run) hoặc Shift + F10
- Hoặc: Run → Run 'Django Server'

**Trong Terminal:**
```bash
python manage.py runserver
```

### Truy cập Admin Panel

1. Truy cập: http://127.0.0.1:8000/admin/
2. Đăng nhập với superuser đã tạo

### Các lệnh Django thường dùng

```bash
# Tạo migrations
python manage.py makemigrations

# Chạy migrations
python manage.py migrate

# Tạo superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test

# Django shell
python manage.py shell

# Load data từ fixture
python manage.py loaddata fixtures/initial_data.json
```

---

## 📁 Cấu trúc dự án

```
<Main-Dir>/
│
├── apps/                       # Django apps
│   ├── accounts/              # User authentication
│   ├── products/              # Product management
│   ├── cart/                  # Shopping cart
│   ├── orders/                # Order management
│   └── reviews/               # Reviews & Sentiment Analysis
│
├── config/                    # Django settings
│   ├── __init__.py
│   ├── settings.py            # Main settings
│   ├── urls.py                # URL routing
│   ├── wsgi.py
│   └── asgi.py
│
├── data/                      # Dataset
│   ├── raw/                   # Original dataset
│   └── processed/             # Processed data
│
├── ml_models/                 # ML models & scripts
│   ├── sentiment_model.bin    # Trained fastText model
│   ├── train_model.py         # Training script
│   └── preprocess.py          # Data preprocessing
│
├── static/                    # Static files (CSS, JS, Images)
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/                 # Django templates
│   ├── base.html
│   ├── accounts/
│   ├── products/
│   ├── cart/
│   ├── orders/
│   └── reviews/
│
├── media/                     # User uploaded files
│
├── venv/                      # Virtual environment
│
├── .env                       # Environment variables (not in Git)
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🤖 Training Sentiment Analysis Model

### Bước 1: Tiền xử lý dữ liệu

**Tạo file `ml_models/preprocess.py`:**

```python
import pandas as pd
from underthesea import word_tokenize
import re

def clean_text(text):
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove special characters
    text = re.sub(r'[^\w\s]', ' ', text)
    # Remove extra spaces
    text = ' '.join(text.split())
    return text.lower()

def preprocess_dataset():
    # Load dataset
    df = pd.read_csv('../data/raw/train.csv')

    # Clean and tokenize
    df['processed_text'] = df['comment'].apply(
        lambda x: word_tokenize(clean_text(str(x)), format="text")
    )

    # Save processed data
    df.to_csv('../data/processed/train_processed.csv', index=False)
    print("Preprocessing completed!")

if __name__ == "__main__":
    preprocess_dataset()
```

**Chạy preprocessing:**
```bash
cd ml_models
python preprocess.py
```

### Bước 2: Training Model

**Tạo file `ml_models/train_model.py`:**

```python
import fasttext
import pandas as pd

def prepare_fasttext_data():
    df = pd.read_csv('../data/processed/train_processed.csv')

    # Format: __label__<class> <text>
    with open('train.txt', 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            label = '__label__positive' if row['sentiment'] > 0 else '__label__negative'
            f.write(f"{label} {row['processed_text']}\n")

def train_model():
    model = fasttext.train_supervised(
        input='train.txt',
        lr=0.1,              # Learning rate
        epoch=25,            # Number of epochs
        wordNgrams=2,        # Use bigrams
        dim=100,             # Vector dimension
        loss='softmax'       # Loss function
    )

    # Save model
    model.save_model('sentiment_model.bin')

    # Test model
    print("Testing model:")
    print(model.predict("Sản phẩm rất tốt, tôi rất hài lòng"))
    print(model.predict("Sản phẩm tệ, không như mô tả"))

    return model

if __name__ == "__main__":
    prepare_fasttext_data()
    train_model()
```

**Chạy training:**
```bash
cd ml_models
python train_model.py
```

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run tests cho một app
python manage.py test apps.products

# Run với coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 📝 TODO

Xem file [PLAN.md](PLAN.md) để biết chi tiết kế hoạch và tiến độ dự án.

---

## 🐛 Troubleshooting

### Lỗi kết nối MySQL

**Lỗi**: `django.db.utils.OperationalError: (2003, "Can't connect to MySQL server")`

**Giải pháp**:
1. Kiểm tra MySQL đang chạy: `sudo systemctl status mysql`
2. Kiểm tra thông tin trong `.env`
3. Test kết nối: `mysql -u ecommerce_user -p`

### Lỗi mysqlclient

**Lỗi**: `OSError: mysql_config not found`

**Giải pháp Windows**:
```bash
pip install mysqlclient-1.4.6-cp39-cp39-win_amd64.whl
# Download wheel file từ: https://www.lfd.uci.edu/~gohlke/pythonlibs/
```

### Lỗi fastText

**Lỗi**: `ImportError: cannot import name 'fasttext'`

**Giải pháp**:
```bash
pip uninstall fasttext
pip install fasttext==0.9.2
```

### Static files không load

**Giải pháp**:
```bash
python manage.py collectstatic --noinput
```

Trong `settings.py`, thêm:
```python
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
```

---

## 📚 Tài liệu tham khảo

- [Django Documentation](https://docs.djangoproject.com/)
- [fastText Documentation](https://fasttext.cc/docs/en/supervised-tutorial.html)
- [Underthesea Documentation](https://underthesea.readthedocs.io/)
- [PyCharm Django Tutorial](https://www.jetbrains.com/help/pycharm/django-support7.html)

---