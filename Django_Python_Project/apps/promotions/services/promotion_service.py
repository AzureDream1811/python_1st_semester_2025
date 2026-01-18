"""
Service Khuyến Mãi cho ElectroShop
==================================

Module này chứa các service xử lý logic nghiệp vụ khuyến mãi:
- Xác thực và áp dụng voucher
- Kiểm tra combo deal
- Quản lý flash sale
- Tạo báo cáo khuyến mãi

Tác giả: ElectroShop Team
"""
from decimal import Decimal
from typing import Dict, Any, List

from django.db import transaction
from django.db.models import F, QuerySet
from django.utils import timezone

from apps.promotions.models import Voucher, VoucherUsage, ComboDeal, FlashSale


class PromotionService:
    """
    Service quản lý các chương trình khuyến mãi
    
    Cung cấp các phương thức:
    - validate_voucher: Xác thực mã voucher
    - calculate_discount: Tính số tiền giảm giá
    - apply_voucher: Áp dụng voucher vào đơn hàng
    - check_combo_deals: Kiểm tra combo deal áp dụng được
    - create_voucher: Tạo voucher mới
    - get_promotion_report: Tạo báo cáo khuyến mãi
    - get_active_flash_sales: Lấy danh sách flash sale đang diễn ra
    """

    @staticmethod
    def validate_voucher(code: str, cart_total: Decimal, user=None) -> Dict[str, Any]:
        """
        Xác thực mã voucher
        
        Kiểm tra các điều kiện:
        - Mã voucher tồn tại
        - Voucher đang active
        - Voucher trong thời gian hiệu lực
        - Chưa vượt quá giới hạn sử dụng
        - Đơn hàng đạt giá trị tối thiểu
        - User chưa vượt quá giới hạn sử dụng cá nhân
        
        Args:
            code: Mã voucher cần kiểm tra
            cart_total: Tổng giá trị giỏ hàng
            user: User đang sử dụng (optional)
            
        Returns:
            Dict với các key:
            - valid: True/False
            - error: Thông báo lỗi (nếu không hợp lệ)
            - voucher: Object voucher (nếu hợp lệ)
            - discount_type: Loại giảm giá
            - discount_value: Giá trị giảm
        """
        try:
            # Tìm voucher theo mã (không phân biệt hoa thường)
            voucher = Voucher.objects.get(code=code.upper())
        except Voucher.DoesNotExist:
            return {'valid': False, 'error': 'Mã voucher không tồn tại'}

        now = timezone.now()

        # Kiểm tra trạng thái active
        if not voucher.is_active:
            return {'valid': False, 'error': 'Mã voucher đã bị vô hiệu hóa'}

        # Kiểm tra thời gian hiệu lực
        if now < voucher.valid_from:
            return {'valid': False, 'error': 'Mã voucher chưa có hiệu lực'}

        if now > voucher.valid_until:
            return {'valid': False, 'error': 'Mã voucher đã hết hạn'}

        # Kiểm tra giới hạn sử dụng tổng
        if voucher.usage_limit > 0 and voucher.used_count >= voucher.usage_limit:
            return {'valid': False, 'error': 'Mã voucher đã hết lượt sử dụng'}

        # Kiểm tra giá trị đơn hàng tối thiểu
        if cart_total < voucher.min_order_value:
            return {
                'valid': False,
                'error': f'Đơn hàng tối thiểu {voucher.min_order_value:,.0f}đ'
            }

        # Kiểm tra giới hạn sử dụng mỗi người
        if user and voucher.usage_limit_per_user > 0:
            user_usage = VoucherUsage.objects.filter(
                voucher=voucher,
                user=user
            ).count()
            if user_usage >= voucher.usage_limit_per_user:
                return {'valid': False, 'error': 'Bạn đã sử dụng hết lượt cho mã này'}

        # Voucher hợp lệ
        return {
            'valid': True,
            'voucher': voucher,
            'discount_type': voucher.discount_type,
            'discount_value': voucher.discount_value
        }

    @staticmethod
    def calculate_discount(voucher: Voucher, cart_total: Decimal) -> Decimal:
        """
        Tính số tiền giảm giá
        
        Hỗ trợ 2 loại giảm giá:
        - percentage: Giảm theo phần trăm tổng đơn
        - fixed: Giảm số tiền cố định
        
        Áp dụng các ràng buộc:
        - Không vượt quá max_discount (nếu có)
        - Không vượt quá tổng giá trị đơn hàng
        
        Args:
            voucher: Object voucher
            cart_total: Tổng giá trị giỏ hàng
            
        Returns:
            Decimal: Số tiền được giảm
        """
        # Tính giảm giá theo loại
        if voucher.discount_type == 'percentage':
            # Giảm theo phần trăm
            discount = cart_total * voucher.discount_value / 100
        else:
            # Giảm số tiền cố định
            discount = voucher.discount_value

        # Áp dụng giới hạn giảm tối đa
        if voucher.max_discount and discount > voucher.max_discount:
            discount = voucher.max_discount

        # Giảm giá không được vượt quá tổng đơn
        if discount > cart_total:
            discount = cart_total

        return discount

    @staticmethod
    def apply_voucher(
            code: str,
            cart_total: Decimal,
            user=None,
            order=None
    ) -> Dict[str, Any]:
        """
        Áp dụng voucher vào đơn hàng
        
        Thực hiện:
        1. Xác thực voucher
        2. Tính số tiền giảm
        3. Ghi nhận lịch sử sử dụng (nếu có order)
        4. Cập nhật số lần sử dụng voucher
        
        Args:
            code: Mã voucher
            cart_total: Tổng giá trị giỏ hàng
            user: User sử dụng (optional)
            order: Đơn hàng áp dụng (optional)
            
        Returns:
            Dict với kết quả áp dụng voucher
        """
        # Bước 1: Xác thực voucher
        validation = PromotionService.validate_voucher(code, cart_total, user)

        if not validation['valid']:
            return validation

        voucher = validation['voucher']

        # Bước 2: Tính số tiền giảm
        discount = PromotionService.calculate_discount(voucher, cart_total)

        # Bước 3 & 4: Ghi nhận sử dụng và cập nhật counter
        if order and user:
            with transaction.atomic():
                # Tạo bản ghi lịch sử sử dụng
                VoucherUsage.objects.create(
                    voucher=voucher,
                    user=user,
                    order=order,
                    discount_amount=discount
                )
                # Tăng số lần sử dụng
                voucher.used_count += 1
                voucher.save(update_fields=['used_count'])

        return {
            'valid': True,
            'discount': discount,
            'voucher_code': voucher.code,
            'voucher_name': voucher.name
        }

    @staticmethod
    def check_combo_deals(cart_items: List[Dict]) -> List[Dict[str, Any]]:
        """
        Kiểm tra và trả về các combo deal có thể áp dụng
        
        Tự động phát hiện khi giỏ hàng chứa đủ các sản phẩm
        trong một combo deal đang có hiệu lực.
        
        Args:
            cart_items: Danh sách sản phẩm trong giỏ hàng
                       Mỗi item cần có key 'product_id'
                       
        Returns:
            List các combo deal có thể áp dụng, mỗi item gồm:
            - combo: Object ComboDeal
            - discount_type: Loại giảm giá
            - discount_value: Giá trị giảm
            - products: Danh sách product_id trong combo
        """
        now = timezone.now()
        applicable_combos = []

        # Lấy danh sách product_id trong giỏ hàng
        cart_product_ids = {item['product_id'] for item in cart_items}

        # Lấy tất cả combo đang có hiệu lực
        combos = ComboDeal.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now
        ).prefetch_related('products')

        # Kiểm tra từng combo
        for combo in combos:
            combo_product_ids = set(combo.products.values_list('id', flat=True))

            # Nếu giỏ hàng chứa tất cả sản phẩm trong combo
            if combo_product_ids.issubset(cart_product_ids):
                applicable_combos.append({
                    'combo': combo,
                    'discount_type': combo.discount_type,
                    'discount_value': combo.discount_value,
                    'products': list(combo_product_ids)
                })

        return applicable_combos

    @staticmethod
    def create_voucher(config: Dict[str, Any]) -> Voucher:
        """
        Tạo voucher mới với cấu hình đầy đủ
        
        Args:
            config: Dict chứa cấu hình voucher:
                - code: Mã voucher (bắt buộc)
                - name: Tên voucher (bắt buộc)
                - description: Mô tả (optional)
                - discount_type: 'percentage' hoặc 'fixed' (bắt buộc)
                - discount_value: Giá trị giảm (bắt buộc)
                - min_order_value: Giá trị đơn tối thiểu (default: 0)
                - max_discount: Giảm tối đa (optional)
                - usage_limit: Giới hạn sử dụng (default: 0 = không giới hạn)
                - usage_limit_per_user: Giới hạn/người (default: 1)
                - valid_from: Ngày bắt đầu (bắt buộc)
                - valid_until: Ngày kết thúc (bắt buộc)
                - is_active: Trạng thái (default: True)
                
        Returns:
            Voucher: Object voucher vừa tạo
        """
        return Voucher.objects.create(
            code=config['code'].upper(),  # Chuyển thành chữ hoa
            name=config['name'],
            description=config.get('description', ''),
            discount_type=config['discount_type'],
            discount_value=config['discount_value'],
            min_order_value=config.get('min_order_value', 0),
            max_discount=config.get('max_discount'),
            usage_limit=config.get('usage_limit', 0),
            usage_limit_per_user=config.get('usage_limit_per_user', 1),
            valid_from=config['valid_from'],
            valid_until=config['valid_until'],
            is_active=config.get('is_active', True)
        )

    @staticmethod
    def get_promotion_report(start_date, end_date) -> Dict[str, Any]:
        """
        Tạo báo cáo khuyến mãi theo khoảng thời gian
        
        Thống kê:
        - Tổng số voucher đã sử dụng
        - Tổng số tiền giảm giá
        - Chi tiết theo từng voucher
        
        Args:
            start_date: Ngày bắt đầu
            end_date: Ngày kết thúc
            
        Returns:
            Dict chứa báo cáo:
            - period: Khoảng thời gian
            - total_vouchers_used: Tổng số voucher đã dùng
            - total_discount: Tổng tiền giảm
            - by_voucher: Thống kê theo từng voucher
        """
        # Lấy tất cả lịch sử sử dụng trong khoảng thời gian
        usages = VoucherUsage.objects.filter(
            used_at__date__gte=start_date,
            used_at__date__lte=end_date
        ).select_related('voucher')

        # Tính tổng
        total_vouchers_used = usages.count()
        total_discount = sum(u.discount_amount for u in usages)

        # Thống kê theo từng voucher
        voucher_stats = {}
        for usage in usages:
            code = usage.voucher.code
            if code not in voucher_stats:
                voucher_stats[code] = {
                    'name': usage.voucher.name,
                    'count': 0,
                    'total_discount': Decimal('0')
                }
            voucher_stats[code]['count'] += 1
            voucher_stats[code]['total_discount'] += usage.discount_amount

        return {
            'period': {'start': start_date, 'end': end_date},
            'total_vouchers_used': total_vouchers_used,
            'total_discount': total_discount,
            'by_voucher': voucher_stats
        }

    @staticmethod
    def get_active_flash_sales() -> QuerySet[FlashSale]:
        """
        Lấy danh sách Flash Sale đang diễn ra
        
        Điều kiện:
        - Flash sale đang active
        - Đã bắt đầu (start_time <= now)
        - Chưa kết thúc (end_time >= now)
        - Còn hàng (sold_count < quantity_limit)
        
        Returns:
            QuerySet[FlashSale]: Danh sách flash sale đang diễn ra
        """
        now = timezone.now()
        return FlashSale.objects.filter(
            is_active=True,
            start_time__lte=now,
            end_time__gte=now,
            sold_count__lt=F('quantity_limit')
        ).select_related('product')
