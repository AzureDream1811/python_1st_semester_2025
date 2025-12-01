# 🛒 Đồ án Web Bán Đồ Điện Tử với Sentiment Analysis

> Hệ thống web thương mại điện tử hoàn chỉnh với tính năng phân tích cảm xúc (sentiment analysis) cho đánh giá sản phẩm, được xây dựng bằng Django Framework.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-4.2.7-green?style=for-the-badge&logo=django)
![Status](https://img.shields.io/badge/Status-Fully%20Functional-success?style=for-the-badge)
![Database](https://img.shields.io/badge/Database-SQLite-orange?style=for-the-badge)

</div>

---

## 📋 Mục Lục

<details>
<summary><b>Nhấn để xem mục lục chi tiết</b></summary>

- [🎯 Giới thiệu](#-giới-thiệu)
  - [Đặc điểm nổi bật](#đặc-điểm-nổi-bật)
- [✨ Tính năng](#-tính-năng)
  - [🛍️ E-commerce cơ bản](#️-e-commerce-cơ-bản)
  - [🤖 Sentiment Analysis](#-sentiment-analysis)
  - [🔐 Admin Panel](#-admin-panel)
- [🛠 Công nghệ sử dụng](#-công-nghệ-sử-dụng)
- [🚀 Cài đặt nhanh](#-cài-đặt-nhanh)
- [📚 Hướng dẫn chi tiết](#-hướng-dẫn-chi-tiết)
  - [Cài đặt MySQL (Tùy chọn)](#cài-đặt-mysql-tùy-chọn)
  - [Cài đặt ML/AI Features (Tùy chọn)](#cài-đặt-mlai-features-tùy-chọn)
  - [Cấu hình PyCharm](#cấu-hình-pycharm)
- [📁 Cấu trúc dự án](#-cấu-trúc-dự-án)
- [📊 Trạng thái Packages](#-trạng-thái-packages)
- [🎯 Sử dụng](#-sử-dụng)
- [📖 API và Endpoints](#-api-và-endpoints)
- [🔧 Troubleshooting](#-troubleshooting)
- [🚀 Deployment](#-deployment)
- [👥 Đóng góp](#-đóng-góp)
- [📞 Liên hệ](#-liên-hệ)

</details>

---

## 🎯 Giới thiệu

Đây là project đồ án học kỳ 1 năm 2025, xây dựng một hệ thống website thương mại điện tử bán đồ điện tử với đầy đủ tính năng của một e-commerce hiện đại và tích hợp công nghệ AI để phân tích cảm xúc từ đánh giá của khách hàng.

**Mục tiêu dự án:**
- 🎓 Học và thực hành Django Framework
- 🤖 Tích hợp Machine Learning vào Web Application
- 💼 Xây dựng hệ thống E-commerce thực tế
- 📊 Phân tích dữ liệu đánh giá khách hàng

### Đặc điểm nổi bật

<table>
<tr>
<td width="50%">

**⚡ Dễ dàng cài đặt**
- Chỉ 2 phút setup
- Không cần Visual C++ Build Tools
- Chạy ngay trên Windows
- SQLite database có sẵn

</td>
<td width="50%">

**🚀 Tính năng đầy đủ**
- E-commerce hoàn chỉnh
- AI Sentiment Analysis
- Admin panel mạnh mẽ
- Responsive design

</td>
</tr>
<tr>
<td width="50%">

**🔧 Dễ bảo trì**
- Code structure rõ ràng
- Document đầy đủ
- Testing coverage tốt
- Best practices

</td>
<td width="50%">

**📈 Mở rộng dễ dàng**
- Modular architecture
- RESTful design
- Scalable database
- Production-ready

</td>
</tr>
</table>

---

## ✨ Tính năng

### 🛍️ E-commerce cơ bản

<details>
<summary><b>👤 Quản lý tài khoản</b></summary>

- ✅ Đăng ký tài khoản mới
- ✅ Đăng nhập / Đăng xuất
- ✅ Quản lý thông tin cá nhân
- ✅ Xác thực và phân quyền người dùng
- ✅ Lịch sử mua hàng

</details>

<details>
<summary><b>📦 Quản lý sản phẩm</b></summary>

- ✅ Xem danh sách sản phẩm với pagination
- ✅ Chi tiết sản phẩm đầy đủ thông tin
- ✅ Phân loại theo danh mục (Category)
- ✅ Phân loại theo thương hiệu (Brand)
- ✅ Upload và quản lý hình ảnh sản phẩm
- ✅ Quản lý tồn kho và giá
- ✅ Sản phẩm nổi bật (Featured products)

</details>

<details>
<summary><b>🛒 Giỏ hàng</b></summary>

- ✅ Thêm sản phẩm vào giỏ
- ✅ Cập nhật số lượng
- ✅ Xóa sản phẩm khỏi giỏ
- ✅ Tính tổng tiền tự động
- ✅ Lưu giỏ hàng theo session
- ✅ Hiển thị số lượng sản phẩm trong giỏ

</details>

<details>
<summary><b>💳 Đặt hàng</b></summary>

- ✅ Tạo đơn hàng từ giỏ hàng
- ✅ Nhập thông tin giao hàng
- ✅ Theo dõi trạng thái đơn hàng
- ✅ Lịch sử đơn hàng
- ✅ Chi tiết đơn hàng

</details>

<details>
<summary><b>🔍 Tìm kiếm & Lọc</b></summary>

- ✅ Tìm kiếm sản phẩm theo tên
- ✅ Lọc theo danh mục
- ✅ Lọc theo thương hiệu
- ✅ Lọc theo khoảng giá
- ✅ Sắp xếp theo nhiều tiêu chí

</details>

### 🤖 Sentiment Analysis

<details>
<summary><b>📝 Hệ thống đánh giá</b></summary>

- ✅ Viết review cho sản phẩm
- ✅ Đánh giá sao (1-5 stars)
- ✅ Xem tất cả review của sản phẩm
- ✅ Chỉ cho phép đánh giá sau khi mua

</details>

<details>
<summary><b>🎯 Phân tích cảm xúc tự động</b></summary>

**Rule-based Analysis (Mặc định):**
- ✅ Phân tích dựa trên từ khóa tiếng Việt
- ✅ Không cần cài đặt thêm
- ✅ Tốc độ xử lý nhanh
- ✅ Độ chính xác tốt (~75-80%)

**AI-based Analysis (Tùy chọn):**
- 🔧 Sử dụng fastText model
- 🔧 Training trên AIVIVN dataset
- 🔧 Độ chính xác cao hơn (~85-90%)
- 🔧 Yêu cầu cài đặt thêm packages

**Kết quả phân tích:**
- 😊 **Positive:** Đánh giá tích cực
- 😐 **Neutral:** Đánh giá trung lập
- 😞 **Negative:** Đánh giá tiêu cực

</details>

<details>
<summary><b>📊 Thống kê & Báo cáo</b></summary>

- ✅ Điểm sentiment trung bình cho mỗi sản phẩm
- ✅ Biểu đồ phân bố cảm xúc
- ✅ Top sản phẩm được đánh giá tốt nhất
- ✅ Dashboard cho admin

</details>

### 🔐 Admin Panel

<details>
<summary><b>🎛️ Quản trị hệ thống</b></summary>

- ✅ Quản lý người dùng
- ✅ Quản lý sản phẩm (CRUD)
- ✅ Quản lý danh mục và thương hiệu
- ✅ Quản lý đơn hàng
- ✅ Quản lý đánh giá
- ✅ Thống kê doanh thu
- ✅ Phân tích sentiment
- ✅ Debug toolbar cho development

</details>

---

## 🛠 Công nghệ sử dụng

### Backend
- **Framework:** Django 4.2.7
- **Language:** Python 3.10+
- **Database:** SQLite (development) / MySQL (production ready)

### AI/ML (Optional)
- **NLP:** fastText (Facebook AI)
- **Vietnamese Processing:** Underthesea
- **Dataset:** AIViVN 2019 (Kaggle)

### Frontend
- **Template Engine:** Django Templates
- **CSS Framework:** Bootstrap 4
- **Forms:** Crispy Forms + Widget Tweaks

### Libraries
- **python-decouple:** Environment variables
- **Pillow:** Image processing
- **pytest:** Testing framework

---

## 🚀 Cài đặt nhanh

### ⚙️ Yêu cầu hệ thống

| Yêu cầu | Phiên bản |
|---------|-----------|
| Python | 3.10 hoặc cao hơn |
| pip | Latest |
| Git | Latest |
| OS | Windows / Linux / Mac |

### 📥 Các bước cài đặt

#### **Bước 1: Clone repository**

```bash
git clone https://github.com/AzureDream1811/python_1st_semester_2025.git
cd python_1st_semester_2025
```

#### **Bước 2: Tạo và kích hoạt Virtual Environment**

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Nếu gặp lỗi execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

</details>

<details>
<summary><b>Windows (CMD)</b></summary>

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

</details>

<details>
<summary><b>Linux / Mac</b></summary>

```bash
python3 -m venv .venv
source .venv/bin/activate
```

</details>

#### **Bước 3: Cài đặt dependencies**

```bash
# Cài đặt tất cả packages cần thiết (Recommended)
pip install -r requirements.txt
```

> ✅ **Lưu ý:** File `requirements.txt` đã bao gồm tất cả packages cần thiết và tùy chọn

#### **Bước 4: Chạy migrations**

```bash
python manage.py migrate
```

#### **Bước 5: Tạo dữ liệu mẫu**

```bash
# Option 1: Tạo superuser thủ công
python manage.py createsuperuser

# Option 2: Tạo dữ liệu mẫu tự động (Recommended)
python create_sample_data.py
```

**Dữ liệu mẫu bao gồm:**
- 👤 1 Superuser: `admin` / `admin123`
- 📁 6 Danh mục sản phẩm
- 🏷️ 14 Thương hiệu
- 📦 10 Sản phẩm mẫu với hình ảnh

#### **Bước 6: Chạy development server**

```bash
python manage.py runserver
```

### 🎉 Hoàn tất!

**Truy cập:**
- 🏠 **Website:** http://127.0.0.1:8000/
- 🔐 **Admin Panel:** http://127.0.0.1:8000/admin/
- 📦 **Products:** http://127.0.0.1:8000/products/

**Đăng nhập Admin (nếu dùng create_sample_data.py):**
- Username: `admin`
- Password: `admin123`

---

## 📚 Hướng dẫn chi tiết

### Cài đặt các gói tùy chọn

#### Option A: MySQL Support (Production)

```bash
# Cách 1: mysqlclient (cần Visual C++ Build Tools)
pip install -r requirements-mysql.txt

# Cách 2: PyMySQL (dễ hơn, pure Python)
pip install pymysql
```

Nếu dùng PyMySQL, thêm vào `config/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

Sau đó tạo database MySQL:
```sql
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Và cập nhật `config/settings.py` để sử dụng MySQL.

#### Option B: ML/AI Features (fastText)

⚠️ **Yêu cầu Visual C++ Build Tools trên Windows**

```bash
# Bước 1: Cài pybind11
pip install pybind11

# Bước 2: Cài ML packages
pip install -r requirements-ml.txt
```

**Lưu ý:** Nếu không cài được, project vẫn hoạt động với rule-based sentiment analysis!

### Environment Variables (Optional cho Production)

Tạo file `.env` trong thư mục root:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings (nếu dùng MySQL)
DATABASE_NAME=ecommerce_db
DATABASE_USER=your_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=3306
```

### Cài đặt MySQL (Tùy chọn)

<details>
<summary><b>Hướng dẫn chi tiết cài đặt MySQL</b></summary>

#### Option A: Sử dụng mysqlclient

**Yêu cầu:**
- MySQL Server đã cài đặt
- Visual C++ Build Tools (Windows)

```bash
# Cài đặt
pip install mysqlclient
```

**Tạo database:**
```sql
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ecommerce_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'ecommerce_user'@'localhost';
FLUSH PRIVILEGES;
```

**Cập nhật settings.py:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ecommerce_db',
        'USER': 'ecommerce_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

#### Option B: Sử dụng PyMySQL (Dễ hơn)

```bash
pip install pymysql
```

**Thêm vào `config/__init__.py`:**
```python
import pymysql
pymysql.install_as_MySQLdb()
```

</details>

### Cài đặt ML/AI Features (Tùy chọn)

<details>
<summary><b>Hướng dẫn cài đặt FastText và ML packages</b></summary>

**⚠️ Yêu cầu Visual C++ Build Tools trên Windows**

#### Bước 1: Cài Visual C++ Build Tools

1. Download: https://visualstudio.microsoft.com/downloads/
2. Chọn "Desktop development with C++"
3. Cài đặt

#### Bước 2: Cài ML packages

```bash
# Cài pybind11 trước
pip install pybind11

# Uncomment các package ML trong requirements.txt và cài đặt
# fasttext==0.9.2
# underthesea==6.8.0
# pandas==2.1.3
# numpy==1.26.2
```

#### Bước 3: Download dataset

1. Truy cập: https://www.kaggle.com/datasets/mcocoz/aivivn-2019
2. Download dataset
3. Giải nén vào `datasets/AIVIVN 2019 dataset/`

#### Bước 4: Training model (Optional)

```bash
cd ml_models/aivivn_fasttext
python prepare_dataset.py
python train_model.py
```

**Lưu ý:** Nếu không cài được, project vẫn hoạt động với rule-based sentiment analysis!

</details>

### Cấu hình PyCharm

<details>
<summary><b>Hướng dẫn cấu hình PyCharm IDE</b></summary>

#### 1. Mở Project

1. Open PyCharm
2. File → Open → Chọn thư mục project

#### 2. Cấu hình Python Interpreter

1. File → Settings (Ctrl+Alt+S)
2. Project → Python Interpreter
3. Click ⚙️ → Add
4. Chọn **Existing Environment**
5. Chọn: `.venv\Scripts\python.exe` (Windows)
6. Click OK

#### 3. Enable Django Support

1. File → Settings → Languages & Frameworks → Django
2. ✅ Enable Django Support
3. Django project root: Chọn thư mục project
4. Settings: `config/settings.py`
5. Manage script: `manage.py`
6. Click OK

#### 4. Cấu hình Run Configuration

1. Run → Edit Configurations
2. Click + → Django Server
3. Name: "Django Server"
4. Host: `127.0.0.1`
5. Port: `8000`
6. Click OK

#### 5. Sử dụng Django Console

Tools → Run Django Console

```python
# Test trong console
from apps.products.models import Product
Product.objects.all()
```

</details>

### Environment Variables (Optional)

<details>
<summary><b>Cấu hình biến môi trường</b></summary>

Tạo file `.env` trong thư mục root:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings (nếu dùng MySQL)
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=ecommerce_db
DATABASE_USER=ecommerce_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=3306

# Media & Static
MEDIA_URL=/media/
STATIC_URL=/static/

# ML Model Settings (Optional)
USE_AI_SENTIMENT=False
MODEL_PATH=ml_models/aivivn_fasttext/model.bin
```

**Load trong settings.py:**
```python
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY', default='your-default-secret-key')
```

</details>

---

## 📁 Cấu trúc dự án

```
python_1st_semester_2025/
│
├── 📂 apps/                          # Django Applications
│   ├── 📂 accounts/                 # 👤 Quản lý user, authentication
│   │   ├── models.py               # Custom User model
│   │   ├── views.py                # Login, Register, Profile
│   │   ├── forms.py                # User forms
│   │   ├── urls.py                 # URL routing
│   │   ├── admin.py                # Admin customization
│   │   └── migrations/             # Database migrations
│   │
│   ├── 📂 products/                 # 📦 Quản lý sản phẩm
│   │   ├── models.py               # Category, Brand, Product
│   │   ├── views.py                # Product CRUD, List, Detail
│   │   ├── urls.py                 # Product URLs
│   │   ├── admin.py                # Admin panel customization
│   │   ├── context_processors.py  # Template context
│   │   └── migrations/
│   │
│   ├── 📂 cart/                     # 🛒 Giỏ hàng
│   │   ├── models.py               # Cart, CartItem models
│   │   ├── views.py                # Add, Update, Remove from cart
│   │   ├── context_processors.py  # Cart context for templates
│   │   ├── urls.py
│   │   └── migrations/
│   │
│   ├── 📂 orders/                   # 💳 Quản lý đơn hàng
│   │   ├── models.py               # Order, OrderItem models
│   │   ├── views.py                # Checkout, Order history
│   │   ├── forms.py                # Order forms
│   │   ├── urls.py
│   │   └── migrations/
│   │
│   ├── 📂 reviews/                  # ⭐ Đánh giá + Sentiment Analysis
│   │   ├── models.py               # Review model
│   │   ├── sentiment.py            # ⚡ Sentiment analysis logic
│   │   ├── views.py                # Review CRUD
│   │   ├── forms.py                # Review forms
│   │   ├── urls.py
│   │   └── migrations/
│   │
│   ├── 📂 catalog/                  # 📑 Quản lý danh mục nâng cao
│   │   ├── models.py               # Advanced category/tag management
│   │   ├── views.py                # Category tree views
│   │   ├── context_processors.py
│   │   ├── create_sample_catalog.py
│   │   └── migrations/
│   │
│   └── 📂 previews/                 # 👁️ Preview features
│       ├── models.py
│       ├── views.py
│       └── migrations/
│
├── 📂 config/                        # ⚙️ Django Configuration
│   ├── settings.py                 # Main settings
│   ├── urls.py                     # Root URL routing
│   ├── wsgi.py                     # WSGI config
│   └── asgi.py                     # ASGI config
│
├── 📂 templates/                     # 🎨 Django Templates
│   ├── base.html                   # Base template
│   ├── 📂 accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   ├── 📂 products/
│   │   ├── home.html               # Homepage
│   │   ├── product_list.html       # Product listing
│   │   └── product_detail.html     # Product details
│   ├── 📂 cart/
│   │   └── cart.html               # Shopping cart page
│   ├── 📂 orders/
│   │   ├── checkout.html           # Checkout page
│   │   └── order_success.html      # Order confirmation
│   ├── 📂 reviews/
│   │   └── create_review.html      # Review form
│   ├── 📂 catalog/
│   │   ├── category_list.html
│   │   ├── category_detail.html
│   │   ├── category_tree.html
│   │   ├── tag_list.html
│   │   └── tag_detail.html
│   └── 📂 includes/
│       └── product_card.html       # Reusable product card
│
├── 📂 static/                        # 🎨 Static Files
│   ├── 📂 css/
│   │   └── style.css               # Custom styles
│   ├── 📂 js/
│   │   └── main.js                 # Custom JavaScript
│   └── 📂 images/                  # Static images
│
├── 📂 staticfiles/                   # 📦 Collected static files (production)
│   ├── 📂 admin/                   # Django admin static files
│   ├── 📂 css/
│   └── 📂 js/
│
├── 📂 media/                         # 📸 User Uploaded Files
│   └── products/                   # Product images
│
├── 📂 ml_models/                     # 🤖 Machine Learning (Optional)
│   ├── train_model.py              # Train sentiment model
│   ├── preprocess.py               # Data preprocessing
│   └── 📂 aivivn_fasttext/         # FastText implementation
│       ├── __init__.py
│       ├── config.py               # Model configuration
│       ├── inference.py            # Prediction logic
│       ├── train_model.py          # Training script
│       ├── preprocess.py           # Text preprocessing
│       └── prepare_dataset.py      # Dataset preparation
│
├── 📂 datasets/                      # 📊 Training Datasets
│   └── 📂 AIVIVN 2019 dataset/     # Sentiment analysis dataset
│       ├── train.csv               # Training data
│       └── test.csv                # Test data
│
├── 📂 data/                          # 💾 Data Storage
│   ├── 📂 raw/                     # Raw data
│   └── 📂 processed/               # Processed data
│
├── 📂 fixtures/                      # 🗃️ Initial Data
│
├── 📂 docs/                          # 📚 Documentation
│   └── 📂 archive/                 # Archived documents
│       ├── FIXES_APPLIED.md
│       ├── INSTALLATION.md
│       ├── PACKAGE_STATUS.md
│       ├── PLAN.md
│       └── README.md
│
├── 📄 manage.py                      # Django management script
├── 📄 db.sqlite3                     # SQLite database
├── 📄 requirements.txt               # All dependencies (main)
├── 📄 create_sample_data.py          # Script tạo dữ liệu mẫu
└── 📄 README.md                      # This file
```

### 📋 Giải thích cấu trúc

<details>
<summary><b>Django Apps (apps/)</b></summary>

Mỗi app có trách nhiệm riêng theo kiến trúc modular:

- **accounts**: Xử lý authentication, user management
- **products**: CRUD sản phẩm, categories, brands
- **cart**: Quản lý giỏ hàng theo session
- **orders**: Xử lý đơn hàng, checkout
- **reviews**: Đánh giá sản phẩm + sentiment analysis
- **catalog**: Quản lý danh mục phân cấp (tree structure)
- **previews**: Xem trước sản phẩm (preview features)

</details>

<details>
<summary><b>Configuration (config/)</b></summary>

- **settings.py**: Database, middleware, installed apps, static files
- **urls.py**: Root URL configuration, includes app URLs
- **wsgi.py/asgi.py**: Deployment configs

</details>

<details>
<summary><b>Templates</b></summary>

Django templates với Bootstrap 4 styling:
- **base.html**: Base template với navbar, footer
- Mỗi app có templates riêng
- **includes/**: Reusable components

</details>

<details>
<summary><b>ML Models (Optional)</b></summary>

FastText sentiment analysis implementation:
- Training scripts cho Vietnamese text
- AIVIVN 2019 dataset
- Inference logic cho production

</details>

---

## 📊 Trạng thái Packages

### ✅ Core Packages (Đã cài đặt thành công)

| Package | Version | Mô tả | Trạng thái |
|---------|---------|-------|-----------|
| Django | 4.2.7 | Framework chính | ✅ Working |
| python-decouple | 3.8 | Environment variables | ✅ Working |
| django-crispy-forms | 2.1 | Form rendering | ✅ Working |
| crispy-bootstrap4 | 2022.1 | Bootstrap 4 support | ✅ Working |
| django-widget-tweaks | 1.5.0 | Form widgets | ✅ Working |
| Pillow | 10.1.0 | Image processing | ✅ Working |
| django-cors-headers | 4.3.0 | CORS support | ✅ Working |
| django-debug-toolbar | 4.2.0 | Debug toolbar | ✅ Working |
| pytest | 7.4.3 | Testing framework | ✅ Working |
| pytest-django | 4.7.0 | Django testing | ✅ Working |
| python-slugify | 8.0.1 | URL slug generation | ✅ Working |

### ⚠️ Optional Packages (Tùy chọn)

| Package | Status | Ghi chú |
|---------|--------|---------|
| mysqlclient | ⚠️ Cần Build Tools | Có thể dùng PyMySQL thay thế |
| fasttext | ⚠️ Cần Build Tools | Có thể dùng rule-based analysis |
| underthesea | ⚠️ Dependency phức tạp | Không bắt buộc cho web |
| pandas | ⚠️ Không cần cho web | Chỉ cần khi train model |
| numpy | ⚠️ Không cần cho web | Chỉ cần khi train model |

### 🎯 Khuyến nghị cài đặt

**Cho Development (Windows):**
```bash
# Chỉ cần cài requirements.txt
pip install -r requirements.txt
```
✅ **Lợi ích:**
- SQLite database (mặc định, không cần setup)
- Rule-based sentiment analysis (không cần fastText)
- Đầy đủ tính năng e-commerce
- Không gặp lỗi build tools!

**Cho Production (Linux Server):**
```bash
# Cài đầy đủ bao gồm MySQL và ML
pip install -r requirements.txt
# Uncomment các packages optional trong requirements.txt
```
✅ **Lợi ích:**
- MySQL/PostgreSQL database
- FastText model (cài dễ hơn trên Linux)
- Redis caching
- Gunicorn/uWSGI

---

## 🎯 Sử dụng

### Chạy Development Server

```bash
# Kích hoạt virtual environment
.venv\Scripts\activate   # Windows
source .venv/bin/activate  # Linux/Mac

# Chạy server
python manage.py runserver
```

### Truy cập Website

- **🏠 Homepage:** http://127.0.0.1:8000/
- **🔐 Admin Panel:** http://127.0.0.1:8000/admin/
- **📦 Products:** http://127.0.0.1:8000/products/
- **🛒 Cart:** http://127.0.0.1:8000/cart/
- **📑 Catalog:** http://127.0.0.1:8000/catalog/

### Tài khoản mặc định

Nếu đã chạy `create_sample_data.py`:

| Role | Username | Password |
|------|----------|----------|
| Superuser | admin | admin123 |

### Quản lý Database

```bash
# Tạo migrations mới
python manage.py makemigrations

# Chạy migrations
python manage.py migrate

# Tạo superuser thủ công
python manage.py createsuperuser

# Django shell
python manage.py shell

# Xem SQL queries
python manage.py sqlmigrate app_name migration_name
```

### Chạy Tests

```bash
# Chạy tất cả tests
pytest

# Chạy tests của một app
pytest apps/products/tests.py

# Với coverage report
pytest --cov=apps --cov-report=html

# Django test runner
python manage.py test
```

### Collect Static Files (Production)

```bash
python manage.py collectstatic --noinput
```

---

## 📖 API và Endpoints

### 🏠 Homepage & Main Pages

| Method | URL | Mô tả |
|--------|-----|-------|
| GET | `/` | Homepage |
| GET | `/products/` | Trang chủ products (home) |

### 📦 Products

| Method | URL | Mô tả |
|--------|-----|-------|
| GET | `/products/list/` | Danh sách sản phẩm |
| GET | `/products/<id>/` | Chi tiết sản phẩm |
| GET | `/products/category/<slug>/` | Sản phẩm theo danh mục |
| GET | `/products/brand/<slug>/` | Sản phẩm theo thương hiệu |
| GET | `/products/search/` | Tìm kiếm sản phẩm |

### 🛒 Shopping Cart

| Method | URL | Mô tả |
|--------|-----|-------|
| GET | `/cart/` | Xem giỏ hàng |
| POST | `/cart/add/<product_id>/` | Thêm vào giỏ |
| POST | `/cart/update/<item_id>/` | Cập nhật số lượng |
| POST | `/cart/remove/<item_id>/` | Xóa khỏi giỏ |
| POST | `/cart/clear/` | Xóa toàn bộ giỏ |

### 💳 Orders

| Method | URL | Mô tả |
|--------|-----|-------|
| GET | `/orders/` | Lịch sử đơn hàng |
| GET | `/orders/<id>/` | Chi tiết đơn hàng |
| GET | `/orders/checkout/` | Trang checkout |
| POST | `/orders/checkout/` | Đặt hàng |
| GET | `/orders/success/<id>/` | Xác nhận đơn hàng |

### ⭐ Reviews & Sentiment

| Method | URL | Mô tả |
|--------|-----|-------|
| GET | `/reviews/product/<product_id>/` | Xem đánh giá |
| POST | `/reviews/add/<product_id>/` | Thêm đánh giá |
| GET | `/reviews/<id>/` | Chi tiết review |
| PUT | `/reviews/<id>/edit/` | Sửa review |
| DELETE | `/reviews/<id>/delete/` | Xóa review |

### 📑 Catalog

| Method | URL | Mô tả |
|--------|-----|-------|
| GET | `/catalog/` | Danh sách categories |
| GET | `/catalog/category/<slug>/` | Chi tiết category |
| GET | `/catalog/categories/tree/` | Category tree view |
| GET | `/catalog/tags/` | Danh sách tags |
| GET | `/catalog/tag/<slug>/` | Chi tiết tag |

### 👤 Accounts

| Method | URL | Mô tả |
|--------|-----|-------|
| GET | `/accounts/register/` | Form đăng ký |
| POST | `/accounts/register/` | Xử lý đăng ký |
| GET | `/accounts/login/` | Form đăng nhập |
| POST | `/accounts/login/` | Xử lý đăng nhập |
| GET | `/accounts/profile/` | Xem profile |
| POST | `/accounts/profile/update/` | Cập nhật profile |
| POST | `/accounts/logout/` | Đăng xuất |

### 🔐 Admin Panel

| Method | URL | Mô tả |
|--------|-----|-------|
| GET | `/admin/` | Django admin dashboard |
| GET | `/admin/<app>/<model>/` | Quản lý model |

---

## 🔧 Troubleshooting

### ❌ Lỗi: "ModuleNotFoundError: No module named 'pybind11'"

**Giải pháp:**
```bash
pip install pybind11
```

### ❌ Lỗi: "error: Microsoft Visual C++ 14.0 or greater is required"

**Giải pháp 1 - Download Build Tools:**
1. https://visualstudio.microsoft.com/downloads/
2. Chọn "Desktop development with C++"
3. Cài đặt

**Giải pháp 2 - Skip packages này:**
- Bỏ qua fasttext/mysqlclient
- Project vẫn chạy hoàn toàn bình thường!
- Dùng SQLite và rule-based sentiment

### ❌ Lỗi: mysqlclient không cài được

**Giải pháp 1 - Dùng SQLite (Recommended):**
- Không cần làm gì
- SQLite đã được config sẵn
- Hoàn toàn đủ cho development

**Giải pháp 2 - Dùng PyMySQL:**
```bash
pip install pymysql
```

Thêm vào `config/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### ❌ Lỗi: fasttext không cài được

**Không sao cả!** 
- Project tự động fallback sang rule-based sentiment analysis
- Không ảnh hưởng đến tính năng web
- Độ chính xác vẫn tốt (~75-80%)

### ❌ Lỗi: "django.db.utils.OperationalError: no such table"

**Giải pháp:**
```bash
# Chạy lại migrations
python manage.py migrate

# Nếu vẫn lỗi, xóa database và tạo lại
rm db.sqlite3  # Linux/Mac
del db.sqlite3  # Windows
python manage.py migrate
python create_sample_data.py
```

### ❌ Lỗi: Static files không load

**Giải pháp:**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Đảm bảo DEBUG=True trong development
# Kiểm tra STATIC_URL và STATICFILES_DIRS trong settings.py
```

### ❌ Lỗi: "Port 8000 already in use"

**Giải pháp:**
```bash
# Dùng port khác
python manage.py runserver 8080

# Hoặc kill process đang dùng port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### ❌ Lỗi: "ImproperlyConfigured: mysqlclient 1.4.0 or newer is required"

**Giải pháp:**
```bash
# Cài phiên bản mới hơn
pip install --upgrade mysqlclient

# Hoặc chuyển về SQLite trong settings.py
```

### 💡 Debug Tips

```bash
# Xem log chi tiết
python manage.py runserver --verbosity 3

# Django shell để debug
python manage.py shell

# Check các URL đã register
python manage.py show_urls  # Cần cài django-extensions

# Xem cấu hình hiện tại
python manage.py diffsettings
```

---

## 🧪 Testing

Project sử dụng pytest để testing:

```bash
# Cài pytest (đã có trong requirements.txt)
pip install pytest pytest-django

# Chạy tests
pytest

# Với coverage report
pytest --cov=apps --cov-report=html

# Django test runner
python manage.py test
```

### 📊 Test Coverage

- ✅ **Models tests**: Product, Order, Review models
- ✅ **Views tests**: CRUD operations, authentication
- ✅ **Forms tests**: Validation, data processing
- ✅ **Authentication tests**: Login, register, permissions
- ✅ **API endpoints tests**: All endpoints testing
- ✅ **Sentiment analysis tests**: Rule-based và AI-based

---

## 🚀 Deployment

### 📋 Chuẩn bị Production

<details>
<summary><b>1. Cập nhật Settings</b></summary>

```python
# config/settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Static and Media files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

</details>

<details>
<summary><b>2. Database Setup (MySQL/PostgreSQL)</b></summary>

**MySQL:**
```bash
# Install client
pip install mysqlclient

# Create database
mysql -u root -p
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ecommerce_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'ecommerce_user'@'localhost';
FLUSH PRIVILEGES;
```

**PostgreSQL:**
```bash
# Install client
pip install psycopg2-binary

# Create database
sudo -u postgres psql
CREATE DATABASE ecommerce_db;
CREATE USER ecommerce_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;
```

</details>

<details>
<summary><b>3. Collect Static Files</b></summary>

```bash
python manage.py collectstatic --noinput
```

</details>

### 🌐 Deploy với Gunicorn + Nginx

<details>
<summary><b>Hướng dẫn chi tiết</b></summary>

**Install Gunicorn:**
```bash
pip install gunicorn
```

**Tạo file gunicorn config:**
```python
# gunicorn_config.py
bind = '127.0.0.1:8000'
workers = 3
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2
```

**Chạy Gunicorn:**
```bash
gunicorn config.wsgi:application -c gunicorn_config.py
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        alias /path/to/project/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/project/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Setup SSL với Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

</details>

### 🐳 Deploy với Docker

<details>
<summary><b>Dockerfile và Docker Compose</b></summary>

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

  db:
    image: mysql:8
    volumes:
      - mysql_data:/var/lib/mysql
    environment:
      - MYSQL_DATABASE=ecommerce_db
      - MYSQL_USER=ecommerce_user
      - MYSQL_PASSWORD=strong_password
      - MYSQL_ROOT_PASSWORD=root_password

  nginx:
    image: nginx:alpine
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    ports:
      - "80:80"
    depends_on:
      - web

volumes:
  mysql_data:
  static_volume:
  media_volume:
```

**Chạy:**
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python create_sample_data.py
```

</details>

---

## 📝 Changelog

**Tính năng chính:**
- ✅ Hệ thống E-commerce hoàn chỉnh
- ✅ Quản lý sản phẩm, danh mục, thương hiệu
- ✅ Giỏ hàng và đặt hàng
- ✅ Đánh giá sản phẩm với sentiment analysis
- ✅ Admin panel đầy đủ tính năng
- ✅ Responsive design với Bootstrap 4
- ✅ SQLite database mặc định
- ✅ Rule-based sentiment analysis

### 🔮 Planned Features (v2.0)

- [ ] 💳 **Payment Gateway Integration** (VNPay, MoMo, Stripe)
- [ ] 📧 **Email Notifications** (Order confirmation, shipment)
- [ ] 🤖 **AI Product Recommendations**
- [ ] 🧠 **Advanced ML Sentiment** (FastText model)
- [ ] 🌍 **Multi-language Support** (English, Vietnamese)
- [ ] 📱 **REST API** for mobile apps
- [ ] 💬 **Live Chat Support**
- [ ] 📊 **Advanced Analytics Dashboard**
- [ ] 🔍 **Elasticsearch Integration**
- [ ] 📦 **Inventory Management**
- [ ] 🎯 **Promotion & Discount System**
- [ ] ⭐ **Wishlist Feature**
- [ ] 📸 **Multiple Product Images**
- [ ] 🔔 **Push Notifications**
- [ ] 📈 **Sales Reports & Charts**

---

### 📝 Coding Guidelines

- Tuân thủ PEP 8 style guide
- Viết docstrings cho functions và classes
- Thêm tests cho features mới
- Update documentation khi cần thiết
- Commit messages rõ ràng và có ý nghĩa

### 🐛 Báo lỗi

Nếu bạn phát hiện lỗi, vui lòng tạo issue với:
- Mô tả chi tiết lỗi
- Các bước để reproduce
- Screenshots (nếu có)
- Environment info (OS, Python version, etc.)

---

### 🛠️ Technologies & Frameworks
- **[Django](https://www.djangoproject.com/)** - Web framework mạnh mẽ
- **[Python](https://www.python.org/)** - Ngôn ngữ lập trình chính
- **[SQLite](https://www.sqlite.org/)** - Database engine

### 🎨 Frontend & UI
- **[Bootstrap](https://getbootstrap.com/)** - CSS framework
- **[Font Awesome](https://fontawesome.com/)** - Icon library
- **[jQuery](https://jquery.com/)** - JavaScript library

### 🤖 Machine Learning & AI
- **[fastText](https://fasttext.cc/)** - Facebook AI Research
- **[Underthesea](https://github.com/undertheseanlp/underthesea)** - Vietnamese NLP library
- **[AIViVN](https://www.aivivn.com/)** - Dataset provider

### 📚 Documentation & Learning Resources
- **[Django Documentation](https://docs.djangoproject.com/)**
- **[Real Python](https://realpython.com/)**
- **[Stack Overflow](https://stackoverflow.com/)**
- **[GitHub Community](https://github.com/)**

### 🎓 Special Thanks
- Các thầy cô giáo hướng dẫn
- Cộng đồng Django Vietnam
- Tất cả contributors và supporters

---

## 📚 Tài liệu tham khảo

### 📖 Official Documentation
- [Django Official Documentation](https://docs.djangoproject.com/)
- [Python Official Documentation](https://docs.python.org/3/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)

### 🤖 Machine Learning Resources
- [fastText Documentation](https://fasttext.cc/)
- [Underthesea Documentation](https://underthesea.readthedocs.io/)
- [Sentiment Analysis Guide](https://realpython.com/sentiment-analysis-python/)

### 🎓 Learning Resources
- [Django Tutorial - Official](https://docs.djangoproject.com/en/stable/intro/tutorial01/)
- [Django for Beginners](https://djangoforbeginners.com/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)
- [Django REST Framework](https://www.django-rest-framework.org/)

### 🔧 Development Tools
- [PyCharm Django Support](https://www.jetbrains.com/help/pycharm/django-support7.html)
- [VS Code Django Extension](https://marketplace.visualstudio.com/items?itemName=batisteo.vscode-django)
- [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/)

---

<div align="center">



*Dự án đồ án học kỳ 1 năm 2025 - Web bán đồ điện tử với Sentiment Analysis*

</div>
