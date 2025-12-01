"""
Script để tạo dữ liệu mẫu cho web bán hàng điện tử
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.products.models import Category, Brand, Product
from decimal import Decimal

User = get_user_model()

def create_superuser():
    """Tạo tài khoản admin"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='System'
        )
        print("✓ Đã tạo superuser: admin/admin123")
    else:
        print("✓ Superuser đã tồn tại")

def create_categories():
    """Tạo danh mục sản phẩm"""
    categories_data = [
        {'name': 'Điện thoại', 'description': 'Điện thoại thông minh'},
        {'name': 'Laptop', 'description': 'Máy tính xách tay'},
        {'name': 'Tablet', 'description': 'Máy tính bảng'},
        {'name': 'Phụ kiện', 'description': 'Phụ kiện điện tử'},
        {'name': 'Tai nghe', 'description': 'Tai nghe và loa'},
        {'name': 'Đồng hồ thông minh', 'description': 'Smartwatch và wearables'},
    ]

    created = 0
    for cat_data in categories_data:
        category, created_flag = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created_flag:
            created += 1

    print(f"✓ Đã tạo {created} danh mục mới")

def create_brands():
    """Tạo thương hiệu"""
    brands_data = [
        'Samsung', 'Apple', 'Xiaomi', 'OPPO', 'Vivo',
        'Dell', 'HP', 'Asus', 'Lenovo', 'Acer',
        'Sony', 'JBL', 'Logitech', 'Anker'
    ]

    created = 0
    for brand_name in brands_data:
        brand, created_flag = Brand.objects.get_or_create(
            name=brand_name,
            defaults={'description': f'Thương hiệu {brand_name}'}
        )
        if created_flag:
            created += 1

    print(f"✓ Đã tạo {created} thương hiệu mới")

def create_products():
    """Tạo sản phẩm mẫu"""
    products_data = [
        {
            'name': 'iPhone 15 Pro Max 256GB',
            'category': 'Điện thoại',
            'brand': 'Apple',
            'price': 32990000,
            'description': 'iPhone 15 Pro Max với chip A17 Pro mạnh mẽ, camera 48MP, màn hình Super Retina XDR 6.7 inch',
            'short_description': 'iPhone mới nhất với hiệu năng vượt trội',
            'stock': 50,
        },
        {
            'name': 'Samsung Galaxy S24 Ultra 512GB',
            'category': 'Điện thoại',
            'brand': 'Samsung',
            'price': 33990000,
            'description': 'Galaxy S24 Ultra với bút S Pen, camera 200MP, màn hình Dynamic AMOLED 2X 6.8 inch',
            'short_description': 'Flagship Android hàng đầu',
            'stock': 45,
        },
        {
            'name': 'Xiaomi 14 Pro 5G 256GB',
            'category': 'Điện thoại',
            'brand': 'Xiaomi',
            'price': 18990000,
            'description': 'Xiaomi 14 Pro với Snapdragon 8 Gen 3, camera Leica 50MP, sạc nhanh 120W',
            'short_description': 'Điện thoại flagship giá tốt',
            'stock': 60,
        },
        {
            'name': 'MacBook Air M2 13 inch 2024',
            'category': 'Laptop',
            'brand': 'Apple',
            'price': 27990000,
            'description': 'MacBook Air với chip M2, 8GB RAM, 256GB SSD, màn hình Liquid Retina 13.6 inch',
            'short_description': 'Laptop mỏng nhẹ, hiệu năng cao',
            'stock': 30,
        },
        {
            'name': 'Dell XPS 15 9530',
            'category': 'Laptop',
            'brand': 'Dell',
            'price': 45990000,
            'description': 'Dell XPS 15 với Intel Core i7-13700H, RTX 4050, 16GB RAM, 512GB SSD',
            'short_description': 'Laptop cao cấp cho dân đồ họa',
            'stock': 20,
        },
        {
            'name': 'iPad Pro M2 11 inch WiFi 128GB',
            'category': 'Tablet',
            'brand': 'Apple',
            'price': 21990000,
            'description': 'iPad Pro với chip M2, màn hình Liquid Retina 11 inch, hỗ trợ Apple Pencil 2',
            'short_description': 'Tablet mạnh mẽ nhất của Apple',
            'stock': 35,
        },
        {
            'name': 'AirPods Pro 2 USB-C',
            'category': 'Tai nghe',
            'brand': 'Apple',
            'price': 6290000,
            'description': 'AirPods Pro thế hệ 2 với chip H2, chống ồn chủ động, âm thanh không gian',
            'short_description': 'Tai nghe true wireless cao cấp',
            'stock': 100,
        },
        {
            'name': 'Sony WH-1000XM5',
            'category': 'Tai nghe',
            'brand': 'Sony',
            'price': 8490000,
            'description': 'Tai nghe over-ear với chống ồn hàng đầu, thời lượng pin 30 giờ',
            'short_description': 'Tai nghe chống ồn tốt nhất',
            'stock': 40,
        },
        {
            'name': 'Apple Watch Series 9 GPS 41mm',
            'category': 'Đồng hồ thông minh',
            'brand': 'Apple',
            'price': 10490000,
            'description': 'Apple Watch Series 9 với chip S9, màn hình Always-On Retina, theo dõi sức khỏe toàn diện',
            'short_description': 'Smartwatch thông minh nhất',
            'stock': 55,
        },
        {
            'name': 'Logitech MX Master 3S',
            'category': 'Phụ kiện',
            'brand': 'Logitech',
            'price': 2490000,
            'description': 'Chuột không dây cao cấp với 8 nút, cảm biến 8000 DPI, pin 70 ngày',
            'short_description': 'Chuột văn phòng tốt nhất',
            'stock': 80,
        },
    ]

    created = 0
    for prod_data in products_data:
        category = Category.objects.filter(name=prod_data['category']).first()
        brand = Brand.objects.filter(name=prod_data['brand']).first()

        if category and brand:
            product, created_flag = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'category': category,
                    'brand': brand,
                    'price': Decimal(str(prod_data['price'])),
                    'description': prod_data['description'],
                    'short_description': prod_data['short_description'],
                    'stock': prod_data['stock'],
                    'is_active': True,
                }
            )
            if created_flag:
                created += 1

    print(f"✓ Đã tạo {created} sản phẩm mới")

def main():
    print("\n🚀 Bắt đầu tạo dữ liệu mẫu...\n")

    create_superuser()
    create_categories()
    create_brands()
    create_products()

    print("\n✅ Hoàn tất! Dữ liệu mẫu đã được tạo thành công.")
    print("\n📌 Thông tin đăng nhập:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n🌐 Chạy server với lệnh: python manage.py runserver")

if __name__ == '__main__':
    main()

