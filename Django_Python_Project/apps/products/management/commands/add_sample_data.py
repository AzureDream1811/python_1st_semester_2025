# products/management/commands/add_sample_data.py

from django.core.management.base import BaseCommand
from apps.products.models import Category, Brand, Product, FlashSale
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Thêm dữ liệu mẫu vào database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Bắt đầu thêm dữ liệu mẫu...')

        # 1. Tạo Categories
        categories_data = [
            {
                'name': 'Điện thoại',
                'description': 'Smartphone và điện thoại di động',
            },
            {
                'name': 'Laptop',
                'description': 'Máy tính xách tay các loại',
            },
            {
                'name': 'Tablet',
                'description': 'Máy tính bảng',
            },
            {
                'name': 'Phụ kiện',
                'description': 'Phụ kiện điện tử',
            },
            {
                'name': 'Tai nghe',
                'description': 'Tai nghe và loa',
            },
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat.name] = cat
            self.stdout.write(f'✓ Category: {cat.name}')

        # 2. Tạo Brands
        brands_data = [
            {'name': 'Apple', 'description': 'Think Different'},
            {'name': 'Samsung', 'description': 'Samsung Electronics'},
            {'name': 'Xiaomi', 'description': 'Mi products'},
            {'name': 'OPPO', 'description': 'OPPO smartphones'},
            {'name': 'Dell', 'description': 'Dell computers'},
            {'name': 'Asus', 'description': 'ASUS technology'},
            {'name': 'Sony', 'description': 'Sony electronics'},
        ]

        brands = {}
        for brand_data in brands_data:
            brand, created = Brand.objects.get_or_create(
                name=brand_data['name'],
                defaults=brand_data
            )
            brands[brand.name] = brand
            self.stdout.write(f'✓ Brand: {brand.name}')

        # 3. Tạo Products
        products_data = [
            {
                'name': 'iPhone 15 Pro Max 256GB',
                'description': 'iPhone 15 Pro Max với chip A17 Pro mạnh mẽ, camera 48MP',
                'category': categories['Điện thoại'],
                'brand': brands['Apple'],
                'price': Decimal('34990000'),
                'sale_price': Decimal('32990000'),
                'stock': 50,
                'specifications': {
                    'Màn hình': '6.7 inch, Super Retina XDR',
                    'Chip': 'Apple A17 Pro',
                    'RAM': '8GB',
                    'Bộ nhớ': '256GB',
                    'Camera': '48MP + 12MP + 12MP',
                    'Pin': '4422mAh',
                },
                'is_featured': True,
            },
            {
                'name': 'Samsung Galaxy S24 Ultra 512GB',
                'description': 'Galaxy S24 Ultra với S Pen tích hợp, camera 200MP',
                'category': categories['Điện thoại'],
                'brand': brands['Samsung'],
                'price': Decimal('33990000'),
                'sale_price': Decimal('31990000'),
                'stock': 30,
                'specifications': {
                    'Màn hình': '6.8 inch, Dynamic AMOLED 2X',
                    'Chip': 'Snapdragon 8 Gen 3',
                    'RAM': '12GB',
                    'Bộ nhớ': '512GB',
                    'Camera': '200MP + 50MP + 12MP + 10MP',
                    'Pin': '5000mAh',
                },
                'is_featured': True,
            },
            {
                'name': 'Xiaomi 14 Pro 256GB',
                'description': 'Xiaomi 14 Pro với camera Leica, sạc nhanh 120W',
                'category': categories['Điện thoại'],
                'brand': brands['Xiaomi'],
                'price': Decimal('18990000'),
                'sale_price': Decimal('16990000'),
                'stock': 45,
                'specifications': {
                    'Màn hình': '6.73 inch, AMOLED',
                    'Chip': 'Snapdragon 8 Gen 3',
                    'RAM': '12GB',
                    'Bộ nhớ': '256GB',
                    'Camera': '50MP + 50MP + 50MP',
                    'Pin': '4880mAh',
                },
            },
            {
                'name': 'MacBook Pro 14 M3 Pro',
                'description': 'MacBook Pro 14 inch với chip M3 Pro mạnh mẽ',
                'category': categories['Laptop'],
                'brand': brands['Apple'],
                'price': Decimal('52990000'),
                'sale_price': Decimal('49990000'),
                'stock': 20,
                'specifications': {
                    'Màn hình': '14.2 inch, Liquid Retina XDR',
                    'Chip': 'Apple M3 Pro',
                    'RAM': '18GB',
                    'SSD': '512GB',
                    'Card đồ họa': 'Integrated',
                    'Pin': 'Lên đến 18 giờ',
                },
                'is_featured': True,
            },
            {
                'name': 'Dell XPS 15 9530',
                'description': 'Dell XPS 15 với Intel Core i7 thế hệ 13',
                'category': categories['Laptop'],
                'brand': brands['Dell'],
                'price': Decimal('45990000'),
                'sale_price': Decimal('42990000'),
                'stock': 15,
                'specifications': {
                    'Màn hình': '15.6 inch, 4K OLED',
                    'CPU': 'Intel Core i7-13700H',
                    'RAM': '32GB',
                    'SSD': '1TB',
                    'Card đồ họa': 'NVIDIA RTX 4060',
                    'Pin': '86WHr',
                },
            },
            {
                'name': 'iPad Pro 12.9 M2 256GB',
                'description': 'iPad Pro với chip M2, màn hình Liquid Retina XDR',
                'category': categories['Tablet'],
                'brand': brands['Apple'],
                'price': Decimal('32990000'),
                'sale_price': Decimal('29990000'),
                'stock': 25,
                'specifications': {
                    'Màn hình': '12.9 inch, Liquid Retina XDR',
                    'Chip': 'Apple M2',
                    'RAM': '8GB',
                    'Bộ nhớ': '256GB',
                    'Camera': '12MP + 10MP',
                },
            },
            {
                'name': 'AirPods Pro 2',
                'description': 'AirPods Pro thế hệ 2 với chống ồn chủ động',
                'category': categories['Tai nghe'],
                'brand': brands['Apple'],
                'price': Decimal('6490000'),
                'sale_price': Decimal('5990000'),
                'stock': 100,
                'specifications': {
                    'Kết nối': 'Bluetooth 5.3',
                    'Chống ồn': 'ANC chủ động',
                    'Pin': 'Lên đến 6 giờ',
                    'Sạc': 'USB-C',
                },
                'is_featured': True,
            },
            {
                'name': 'Sony WH-1000XM5',
                'description': 'Tai nghe chống ồn hàng đầu từ Sony',
                'category': categories['Tai nghe'],
                'brand': brands['Sony'],
                'price': Decimal('8990000'),
                'sale_price': Decimal('7990000'),
                'stock': 40,
                'specifications': {
                    'Kết nối': 'Bluetooth 5.2',
                    'Chống ồn': 'ANC AI-powered',
                    'Pin': 'Lên đến 30 giờ',
                    'Driver': '30mm',
                },
            },
        ]

        products = []
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults=prod_data
            )
            products.append(product)
            self.stdout.write(f'✓ Product: {product.name}')

        # 4. Tạo Flash Sale
        flash_sale = FlashSale.objects.create(
            name='Flash Sale Tết 2026',
            discount_percent=20,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(days=7),
            is_active=True
        )

        # Thêm một vài sản phẩm vào Flash Sale
        flash_sale.products.add(*products[:3])
        self.stdout.write(f'✓ Flash Sale: {flash_sale.name}')

        self.stdout.write(self.style.SUCCESS('\n✅ Hoàn thành! Đã thêm dữ liệu mẫu.'))