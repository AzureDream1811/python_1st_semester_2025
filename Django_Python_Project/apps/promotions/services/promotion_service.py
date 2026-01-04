"""
Promotion Service for ElectroShop
Voucher validation, combo deals, flash sales
"""
from decimal import Decimal
from typing import Dict, Any, List

from django.db import transaction
from django.db.models import F, QuerySet
from django.utils import timezone

from apps.promotions.models import Voucher, VoucherUsage, ComboDeal, FlashSale


class PromotionService:
    """Service for managing promotions"""

    @staticmethod
    def validate_voucher(code: str, cart_total: Decimal, user=None) -> Dict[str, Any]:
        """
        Validate voucher code
        Property 8: Invalid vouchers must return error
        """
        try:
            voucher = Voucher.objects.get(code=code.upper())
        except Voucher.DoesNotExist:
            return {'valid': False, 'error': 'Mã voucher không tồn tại'}

        now = timezone.now()

        # Check if active
        if not voucher.is_active:
            return {'valid': False, 'error': 'Mã voucher đã bị vô hiệu hóa'}

        # Check validity period
        if now < voucher.valid_from:
            return {'valid': False, 'error': 'Mã voucher chưa có hiệu lực'}

        if now > voucher.valid_until:
            return {'valid': False, 'error': 'Mã voucher đã hết hạn'}

        # Check usage limit
        if voucher.usage_limit > 0 and voucher.used_count >= voucher.usage_limit:
            return {'valid': False, 'error': 'Mã voucher đã hết lượt sử dụng'}

        # Check min order value
        if cart_total < voucher.min_order_value:
            return {
                'valid': False,
                'error': f'Đơn hàng tối thiểu {voucher.min_order_value:,.0f}đ'
            }

        # Check per-user limit
        if user and voucher.usage_limit_per_user > 0:
            user_usage = VoucherUsage.objects.filter(
                voucher=voucher,
                user=user
            ).count()
            if user_usage >= voucher.usage_limit_per_user:
                return {'valid': False, 'error': 'Bạn đã sử dụng hết lượt cho mã này'}

        return {
            'valid': True,
            'voucher': voucher,
            'discount_type': voucher.discount_type,
            'discount_value': voucher.discount_value
        }

    @staticmethod
    def calculate_discount(voucher: Voucher, cart_total: Decimal) -> Decimal:
        """
        Calculate discount amount
        Property 9: Discount must be calculated correctly
        """
        if voucher.discount_type == 'percentage':
            discount = cart_total * voucher.discount_value / 100
        else:
            discount = voucher.discount_value

        # Apply max discount cap
        if voucher.max_discount and discount > voucher.max_discount:
            discount = voucher.max_discount

        # Discount cannot exceed cart total
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
        Apply voucher and return discount
        Property 9: Must calculate correct discount amount
        """
        validation = PromotionService.validate_voucher(code, cart_total, user)

        if not validation['valid']:
            return validation

        voucher = validation['voucher']
        discount = PromotionService.calculate_discount(voucher, cart_total)

        # Record usage if order provided
        if order and user:
            with transaction.atomic():
                VoucherUsage.objects.create(
                    voucher=voucher,
                    user=user,
                    order=order,
                    discount_amount=discount
                )
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
        Check and return applicable combo deals
        Property 10: Must auto-apply when cart contains all combo products
        """
        now = timezone.now()
        applicable_combos = []

        cart_product_ids = {item['product_id'] for item in cart_items}

        combos = ComboDeal.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now
        ).prefetch_related('products')

        for combo in combos:
            combo_product_ids = set(combo.products.values_list('id', flat=True))

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
        Create new voucher with full configuration
        """
        return Voucher.objects.create(
            code=config['code'].upper(),
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
        Generate promotion report
        Property 12: Report must match actual usage data
        """
        usages = VoucherUsage.objects.filter(
            used_at__date__gte=start_date,
            used_at__date__lte=end_date
        ).select_related('voucher')

        total_vouchers_used = usages.count()
        total_discount = sum(u.discount_amount for u in usages)

        # Group by voucher
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
        now = timezone.now()
        return FlashSale.objects.filter(
            is_active=True,
            start_time__lte=now,
            end_time__gte=now,
            sold_count__lt=F('quantity_limit')
        ).select_related('product')
