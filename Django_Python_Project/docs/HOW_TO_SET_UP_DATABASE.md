# HƯỚNG DẪN CÀI ĐẶT DJANGO + MYSQL WORKBENCH

---

## MỤC LỤC


0. [Cài đặt MySQL Workbench và MySQL Server](#phần-0-cài-đặt-mysql-workbench-và-mysql-server)
1. [Tạo Database trong MySQL Workbench](#phần-1-tạo-database-trong-mysql-workbench)
2. [Cấu hình Django kết nối MySQL](#phần-2-cấu-hình-django-kết-nối-mysql)
3. [Cài đặt thư viện Python](#phần-3-cài-đặt-thư-viện-python)
4. [Chạy Migrations](#phần-4-chạy-migrations-tạo-bảng)
5. [Tạo tài khoản Admin](#phần-5-tạo-tài-khoản-admin)
6. [Chạy Server](#phần-6-chạy-server)
7. [Xem Database trong MySQL Workbench](#phần-7-xem-database-trong-mysql-workbench)
8. [Xử lý lỗi thường gặp](#phần-8-xử-lý-lỗi-thường-gặp)

---

## PHẦN 0: CÀI ĐẶT MYSQL WORKBENCH VÀ MYSQL SERVER

1. Tải MySQL Installer (mysql-installer-community-8.0.44.0.msi KHÔNG PHẢI WEB) từ: https://dev.mysql.com/downloads/installer/
2. Chạy file cài đặt → Chọn **Custom** → Chọn các package:
   - MySQL Server
   - MySQL Workbench
3. Cài đặt và cấu hình MySQL Server:
   - Chọn Authentication Method: Use Strong Password Encryption
   - Đặt password cho user `root` (ví dụ: `123456`)
   - Chọn **Standard System Account**
   - Hoàn tất cài đặt và khởi động MySQL Server

    
## PHẦN 1: TẠO DATABASE TRONG MYSQL WORKBENCH

### 1.1. Mở MySQL Workbench

1. Mở MySQL Workbench từ Start Menu
2. Click vào connection **"Local instance MySQL80"** (hoặc tên tương tự)
3. Nhập password root → Click **OK**

### 1.2. Tạo Database mới

1. Click vào tab **Query** (hoặc nhấn `Ctrl + T`)
2. Gõ lệnh SQL:

```sql
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. Click nút **Execute** (icon ⚡) hoặc nhấn `Ctrl + Enter`
4. Refresh: Click chuột phải vào SCHEMAS → **Refresh All**
5. Bạn sẽ thấy `ecommerce_db` xuất hiện trong danh sách

---

## PHẦN 2: CẤU HÌNH DJANGO KẾT NỐI MYSQL

### 2.1. Mở file `.env` trong thư mục gốc project
Không dùng .env.example, nếu không có .env thì tạo cùng cấp 

```env
# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-your-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# MySQL Database
DATABASE_NAME=ecommerce_db
DATABASE_USER=root
DATABASE_PASSWORD=123456        # ← Password MySQL của bạn
DATABASE_HOST=localhost
DATABASE_PORT=3306
```

### 2.2. Kiểm tra file `config/settings.py`

File này đã được cấu hình sẵn để đọc từ `.env`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DATABASE_NAME', default='ecommerce_db'),
        'USER': config('DATABASE_USER', default='root'),
        'PASSWORD': config('DATABASE_PASSWORD', default=''),
        'HOST': config('DATABASE_HOST', default='localhost'),
        'PORT': config('DATABASE_PORT', default='3306'),
    }
}
```

---

## PHẦN 3: CÀI ĐẶT THƯ VIỆN PYTHON

### 3.1. Mở Terminal trong thư mục project

```bash
cd "C:\Users\Admin\PycharmProjects\python_1st_semester_2025"
```

### 3.2. Tạo Virtual Environment

```bash
py -m venv venv
```

### 3.3. Kích hoạt Virtual Environment

```bash
# Windows CMD:
venv\Scripts\activate
```


Khi thành công, bạn thấy `(venv)` ở đầu dòng lệnh.

### 3.4. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

---

## PHẦN 4: CHẠY MIGRATIONS (TẠO BẢNG)

### 4.1. Tạo file migrations

```bash
py manage.py makemigrations
```

**Kết quả mong đợi:**
```
Migrations for 'accounts':
  apps\accounts\migrations\0001_initial.py
    - Create model User
    - Create model Address
Migrations for 'products':
  apps\products\migrations\0001_initial.py
    - Create model Category
    - Create model Product
...
```

### 4.2. Áp dụng migrations vào database

```bash
py manage.py migrate
```

**Kết quả mong đợi:**
```
Operations to perform:
  Apply all migrations: accounts, admin, auth, cart, orders, products, reviews, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying accounts.0001_initial... OK
  ...
```

---

## PHẦN 5: TẠO TÀI KHOẢN ADMIN

```bash
py manage.py createsuperuser
```

Nhập thông tin:
```
Username: admin
Email: admin@example.com
Password: admin123
Password (again): admin123
```

---

## PHẦN 6: CHẠY SERVER

### 6.1. Kiểm tra hệ thống

```bash
py manage.py check
```

Nếu hiện `System check identified no issues (0 silenced).` → OK!

### 6.2. Chạy server

```bash
py manage.py runserver
```

### 6.3. Truy cập website

| Trang | URL |
|-------|-----|
| Admin Panel | http://127.0.0.1:8000/admin |
| Trang chủ | http://127.0.0.1:8000 |

**Đăng nhập Admin:**
- Username: `admin`
- Password: `admin123`

---

## PHẦN 7: XEM DATABASE TRONG MYSQL WORKBENCH

### 7.1. Xem danh sách bảng

1. Mở MySQL Workbench → Kết nối vào server
2. Nhìn cột trái → Mở rộng **SCHEMAS**
3. Click **▶** bên cạnh `ecommerce_db`
4. Click **▶** bên cạnh **Tables**

**Danh sách bảng:**
```
ecommerce_db
├── Tables
│   ├── accounts_address
│   ├── accounts_user
│   ├── cart_cart
│   ├── cart_cartitem
│   ├── orders_order
│   ├── orders_orderhistory
│   ├── orders_orderitem
│   ├── products_brand
│   ├── products_category
│   ├── products_product
│   ├── products_productimage
│   ├── products_wishlist
│   ├── reviews_review
│   └── reviews_reviewhelpful
```

### 7.2. Xem dữ liệu trong bảng

**Cách 1:** Click chuột phải vào bảng → **Select Rows - Limit 1000**

**Cách 2:** Viết SQL Query
```sql
-- Xem tất cả users
SELECT * FROM accounts_user;

-- Xem tất cả sản phẩm
SELECT * FROM products_product;

-- Xem tất cả đơn hàng
SELECT * FROM orders_order;
```

### 7.3. Xem cấu trúc bảng

```sql
DESCRIBE accounts_user;
```

### 7.4. Kiểm tra user admin

```sql
SELECT id, username, email, is_staff, is_superuser 
FROM accounts_user 
WHERE username = 'admin';
```

---

## PHẦN 8: XỬ LÝ LỖI THƯỜNG GẶP

### Lỗi 1: "Access denied for user 'root'@'localhost'"
**Nguyên nhân:** Sai password MySQL
**Giải pháp:** Kiểm tra `DATABASE_PASSWORD` trong file `.env`

### Lỗi 2: "Can't connect to MySQL server"
**Nguyên nhân:** MySQL chưa chạy
**Giải pháp:** 
- Gõ `services.msc` trong Run
- Tìm "MySQL80" → Click chuột phải → Start

### Lỗi 3: "Unknown database 'ecommerce_db'"
**Nguyên nhân:** Chưa tạo database
**Giải pháp:** Quay lại Phần 1 để tạo database

### Lỗi 4: "No module named 'crispy_forms'"
**Giải pháp:**
```bash
pip install django-crispy-forms crispy-bootstrap4
```

### Lỗi 5: "No module named 'decouple'"
**Giải pháp:**
```bash
pip install python-decouple
```

---

## TỔNG KẾT LỆNH

```bash
# Kích hoạt môi trường ảo
venv\Scripts\activate

# Cài thư viện
pip install -r requirements.txt

# Tạo migrations
py manage.py makemigrations

# Áp dụng migrations
py manage.py migrate

# Tạo admin
py manage.py createsuperuser

# Kiểm tra hệ thống
py manage.py check

# Chạy server
py manage.py runserver

# Dừng server: Ctrl + C
```



---
