"""
Management command để tạo sample data cho testing:
- 10 Vouchers ngẫu nhiên
- 20 Flash Sales từ sản phẩm hiện có
- 72 Orders với ngày đặt từ năm ngoái đến nay
"""
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from apps.products.models import Product
from apps.promotions.models import Voucher, FlashSale
from apps.orders.models import Order, OrderItem
from apps.cart.models import Cart, CartItem


class Command(BaseCommand):
    help = 'Tạo sample vouchers, flash sales và orders cho testing'

    SAMPLE_USERNAMES = [
        'nguyen_van_a', 'tran_thi_b', 'le_van_c', 'pham_thi_d', 'hoang_van_e',
        'vu_thi_f', 'dang_van_g', 'bui_thi_h', 'do_van_i', 'ngo_thi_k',
        'duong_van_l', 'ly_thi_m', 'truong_van_n', 'dinh_thi_o', 'ha_van_p',
        'mai_thi_q', 'vo_van_r', 'tang_thi_s', 'phan_van_t', 'cao_thi_u',
        'customer_01', 'customer_02', 'customer_03', 'customer_04', 'customer_05',
        'buyer_01', 'buyer_02', 'buyer_03', 'buyer_04', 'buyer_05',
    ]

    VOUCHER_NAMES = [
        ('WELCOME10', 'Giảm 10% cho khách hàng mới', 10, 'percentage'),
        ('SAVE50K', 'Giảm 50.000đ cho đơn từ 500K', 50000, 'fixed'),
        ('SUMMER20', 'Khuyến mãi mùa hè - Giảm 20%', 20, 'percentage'),
        ('FLASH15', 'Flash Sale - Giảm 15%', 15, 'percentage'),
        ('VIP100K', 'Ưu đãi VIP - Giảm 100.000đ', 100000, 'fixed'),
        ('NEWYEAR25', 'Mừng năm mới - Giảm 25%', 25, 'percentage'),
        ('FREESHIP', 'Miễn phí vận chuyển - Giảm 30K', 30000, 'fixed'),
        ('WEEKEND10', 'Ưu đãi cuối tuần - Giảm 10%', 10, 'percentage'),
        ('MEMBER15', 'Thành viên thân thiết - Giảm 15%', 15, 'percentage'),
        ('SPECIAL200K', 'Siêu ưu đãi - Giảm 200.000đ', 200000, 'fixed'),
    ]

    ORDER_STATUSES = ['pending', 'confirmed', 'processing', 'shipping', 'delivered', 'completed']
    PAYMENT_METHODS = ['cod', 'bank_transfer', 'vnpay', 'momo']
    PAYMENT_STATUSES = ['pending', 'paid']

    SHIPPING_ADDRESSES = [
        ('Nguyễn Văn A', '0901234567', '123 Nguyễn Huệ', 'Quận 1', 'TP.HCM'),
        ('Trần Thị B', '0912345678', '456 Lê Lợi', 'Quận 3', 'TP.HCM'),
        ('Lê Văn C', '0923456789', '789 Trần Hưng Đạo', 'Quận 5', 'TP.HCM'),
        ('Phạm Thị D', '0934567890', '321 Hai Bà Trưng', 'Quận 10', 'TP.HCM'),
        ('Hoàng Văn E', '0945678901', '654 Võ Văn Tần', 'Quận 3', 'TP.HCM'),
        ('Vũ Thị F', '0956789012', '987 Điện Biên Phủ', 'Bình Thạnh', 'TP.HCM'),
        ('Đặng Văn G', '0967890123', '147 Cách Mạng Tháng 8', 'Quận 10', 'TP.HCM'),
        ('Bùi Thị H', '0978901234', '258 Nguyễn Thị Minh Khai', 'Quận 1', 'TP.HCM'),
        ('Đỗ Văn I', '0989012345', '369 Lý Tự Trọng', 'Quận 1', 'TP.HCM'),
        ('Ngô Thị K', '0990123456', '741 Pasteur', 'Quận 3', 'TP.HCM'),
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Xoa vouchers, flash sales va orders cu truoc khi tao moi',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Dang xoa du lieu cu...'))
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            FlashSale.objects.all().delete()
            Voucher.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('  Da xoa du lieu cu'))

        # Tạo users nếu chưa có
        self.stdout.write('Dang tao users...')
        users = self.create_users()
        self.stdout.write(self.style.SUCCESS(f'  Da tao/cap nhat {len(users)} users'))

        # Tạo vouchers
        self.stdout.write('Dang tao vouchers...')
        vouchers = self.create_vouchers()
        self.stdout.write(self.style.SUCCESS(f'  Da tao {len(vouchers)} vouchers'))

        # Tạo flash sales
        self.stdout.write('Dang tao flash sales...')
        flash_sales = self.create_flash_sales()
        self.stdout.write(self.style.SUCCESS(f'  Da tao {len(flash_sales)} flash sales'))

        # Tạo orders
        self.stdout.write('Dang tao orders...')
        orders = self.create_orders(users, flash_sales)
        self.stdout.write(self.style.SUCCESS(f'  Da tao {len(orders)} orders'))

        self.stdout.write(self.style.SUCCESS('\n[HOAN THANH] Da tao tat ca sample data!'))

    def create_users(self):
        """Tạo users từ SAMPLE_USERNAMES"""
        users = []
        for username in self.SAMPLE_USERNAMES:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': username.split('_')[0].title(),
                    'last_name': username.split('_')[-1].title() if '_' in username else '',
                    'is_active': True,
                }
            )
            # Set password cho user
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)
        return users

    def create_vouchers(self):
        """Tạo 10 vouchers ngẫu nhiên"""
        vouchers = []
        now = timezone.now()

        for code, description, value, discount_type in self.VOUCHER_NAMES:
            # Random thời hạn
            valid_from = now - timedelta(days=random.randint(0, 30))
            valid_until = now + timedelta(days=random.randint(30, 90))

            # Random giới hạn
            usage_limit = random.choice([50, 100, 200, 500, 0])  # 0 = không giới hạn
            min_order = random.choice([0, 100000, 200000, 500000, 1000000])
            max_discount = None
            if discount_type == 'percentage':
                max_discount = random.choice([100000, 200000, 500000, None])

            voucher, created = Voucher.objects.get_or_create(
                code=code,
                defaults={
                    'name': description,
                    'description': description,
                    'discount_type': discount_type,
                    'discount_value': Decimal(str(value)),
                    'min_order_value': Decimal(str(min_order)),
                    'max_discount': Decimal(str(max_discount)) if max_discount else None,
                    'usage_limit': usage_limit,
                    'used_count': random.randint(0, max(1, usage_limit // 2)),
                    'valid_from': valid_from,
                    'valid_until': valid_until,
                    'is_active': True,
                }
            )
            if created:
                vouchers.append(voucher)

        return vouchers

    def create_flash_sales(self):
        """Tạo 20 flash sales từ sản phẩm hiện có"""
        flash_sales = []
        now = timezone.now()

        # Lấy 20 sản phẩm ngẫu nhiên
        products = list(Product.objects.filter(is_active=True).order_by('?')[:20])

        for product in products:
            # Kiểm tra đã có flash sale chưa
            if FlashSale.objects.filter(product=product, end_time__gt=now).exists():
                continue

            # Random thời gian
            # Một số đã kết thúc, một số đang diễn ra, một số sắp diễn ra
            time_type = random.choice(['past', 'active', 'upcoming'])

            if time_type == 'past':
                start_time = now - timedelta(days=random.randint(10, 30))
                end_time = now - timedelta(days=random.randint(1, 9))
            elif time_type == 'active':
                start_time = now - timedelta(hours=random.randint(1, 48))
                end_time = now + timedelta(hours=random.randint(12, 72))
            else:  # upcoming
                start_time = now + timedelta(hours=random.randint(1, 48))
                end_time = start_time + timedelta(hours=random.randint(24, 72))

            # Random giảm giá
            discount_percent = random.choice([10, 15, 20, 25, 30, 35, 40, 50])

            # Random số lượng
            quantity_limit = random.randint(10, 100)
            sold_count = random.randint(0, quantity_limit - 1) if time_type != 'upcoming' else 0

            flash_sale = FlashSale.objects.create(
                product=product,
                discount_type='percentage',
                discount_percent=discount_percent,
                quantity_limit=quantity_limit,
                sold_count=sold_count,
                start_time=start_time,
                end_time=end_time,
                is_active=True,
            )
            flash_sales.append(flash_sale)

        return flash_sales

    def create_orders(self, users, flash_sales):
        """Tạo 72 orders với ngày từ năm ngoái đến nay"""
        orders = []
        now = timezone.now()
        one_year_ago = now - timedelta(days=365)

        # Lấy tất cả sản phẩm
        products = list(Product.objects.filter(is_active=True))
        if not products:
            self.stdout.write(self.style.ERROR('  Khong co san pham nao!'))
            return orders

        # Flash sale products hiện tại
        active_flash_sales = [fs for fs in flash_sales if fs.is_active and fs.start_time <= now <= fs.end_time]

        for i in range(72):
            # Random user
            user = random.choice(users)

            # Random ngày đặt hàng (từ năm ngoái đến nay)
            days_ago = random.randint(0, 365)
            order_date = now - timedelta(days=days_ago)

            # Random shipping info
            shipping = random.choice(self.SHIPPING_ADDRESSES)

            # Random trạng thái - đơn cũ có xu hướng completed hơn
            if days_ago > 30:
                status = random.choices(
                    self.ORDER_STATUSES,
                    weights=[5, 5, 5, 10, 30, 45],  # Nhiều completed/delivered hơn
                    k=1
                )[0]
            else:
                status = random.choices(
                    self.ORDER_STATUSES,
                    weights=[20, 20, 20, 20, 10, 10],  # Đang xử lý nhiều hơn
                    k=1
                )[0]

            # Payment status dựa vào order status
            if status in ['delivered', 'completed']:
                payment_status = 'paid'
            elif status == 'cancelled':
                payment_status = random.choice(['pending', 'refunded'])
            else:
                payment_status = random.choices(['pending', 'paid'], weights=[30, 70], k=1)[0]

            # Tạo order
            order = Order.objects.create(
                user=user,
                order_number=f'DH{order_date.strftime("%Y%m%d")}{i:04d}',
                status=status,
                payment_method=random.choice(self.PAYMENT_METHODS),
                payment_status=payment_status,
                full_name=shipping[0],
                email=user.email,
                phone=shipping[1],
                address=shipping[2],
                ward=shipping[3],
                district=shipping[3],
                city=shipping[4],
                shipping_fee=Decimal(str(random.choice([0, 15000, 25000, 30000]))),
                note=random.choice(['', 'Giao giờ hành chính', 'Gọi trước khi giao', '']),
                subtotal=Decimal('0'),
                total=Decimal('0'),
            )

            # Cập nhật thời gian tạo
            order.created_at = order_date
            order.save(update_fields=['created_at'])

            # Tạo order items (1-5 sản phẩm mỗi đơn)
            num_items = random.randint(1, 5)
            selected_products = random.sample(products, min(num_items, len(products)))
            subtotal = Decimal('0')

            for product in selected_products:
                quantity = random.randint(1, 3)

                # Kiểm tra có flash sale không (30% cơ hội)
                flash_sale_price = None
                if random.random() < 0.3 and active_flash_sales:
                    # Tìm flash sale của sản phẩm này
                    product_flash_sales = [fs for fs in active_flash_sales if fs.product_id == product.id]
                    if product_flash_sales:
                        fs = product_flash_sales[0]
                        flash_sale_price = fs.get_effective_sale_price()

                # Tính giá
                if flash_sale_price:
                    price = flash_sale_price * quantity
                elif product.sale_price:
                    price = product.sale_price * quantity
                else:
                    price = product.price * quantity

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price,
                )
                subtotal += price

            # Cập nhật tổng tiền
            order.subtotal = subtotal
            order.total = subtotal + order.shipping_fee
            order.save(update_fields=['subtotal', 'total'])

            orders.append(order)

            # Progress
            if (i + 1) % 20 == 0:
                self.stdout.write(f'    Da tao {i + 1}/72 orders')

        return orders
