"""
Views Khuyến Mãi cho ElectroShop
================================

Module này xử lý các request liên quan đến khuyến mãi:
- Flash Sale: Danh sách và chi tiết flash sale
- Combo Deal: Danh sách combo khuyến mãi
- Voucher: Xác thực và áp dụng mã giảm giá

Tác giả: ElectroShop Team
"""
from decimal import Decimal, ROUND_HALF_UP

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Voucher, ComboDeal, FlashSale
from .services.promotion_service import PromotionService


# =============================================================================
# FLASH SALE VIEWS
# =============================================================================

def flash_sale_list(request):
    """
    Hiển thị danh sách Flash Sales đang diễn ra
    
    Chỉ hiển thị các flash sale:
    - Đã bắt đầu (start_time <= now)
    - Chưa kết thúc (end_time >= now)
    - Đang active (is_active=True)
    
    Sắp xếp theo thời gian kết thúc (sắp hết trước)
    
    Template: promotions/flash_sale_list.html
    """
    now = timezone.now()

    # Lấy danh sách flash sale đang diễn ra
    flash_sales = FlashSale.objects.filter(
        start_time__lte=now,  # Đã bắt đầu
        end_time__gte=now,  # Chưa kết thúc
        is_active=True  # Đang hoạt động
    ).select_related('product').order_by('end_time')  # Sắp hết trước

    upcoming_sales = FlashSale.objects.filter(
        start_time__gt=now,
        is_active=True
    ).select_related('product').order_by('start_time')

    context = {
        'flash_sales': flash_sales,
        'now': now,  # Để tính countdown trong template
        'upcoming_sales': upcoming_sales,
    }
    return render(request, 'promotions/flash_sale_list.html', context)


def flash_sale_detail(request, pk):
    """
    Hiển thị chi tiết một Flash Sale
    
    Args:
        pk: ID của flash sale
        
    Template: promotions/flash_sale_detail.html
    """
    flash_sale = get_object_or_404(FlashSale, pk=pk)

    context = {
        'flash_sale': flash_sale,
        'now': timezone.now(),  # Để kiểm tra trạng thái và countdown
    }
    return render(request, 'promotions/flash_sale_detail.html', context)


# =============================================================================
# COMBO DEAL VIEWS
# =============================================================================

def combo_deal_list(request):
    """
    Hiển thị danh sách Combo Deals đang có hiệu lực
    
    Chỉ hiển thị các combo:
    - Đã có hiệu lực (valid_from <= now)
    - Chưa hết hạn (valid_until >= now)
    - Đang active (is_active=True)
    
    Sắp xếp theo ngày tạo mới nhất
    
    Template: promotions/combo_deal_list.html
    """
    now = timezone.now()
    money_round = Decimal('0.01')

    combo_deals_qs = ComboDeal.objects.filter(
        valid_from__lte=now,
        valid_until__gte=now,
        is_active=True
    ).prefetch_related('products', 'products__brand').order_by('-created_at')

    combo_deals = list(combo_deals_qs)
    combo_cards = []
    total_products = 0
    total_discount_percent = Decimal('0')
    next_expiry = None

    for combo in combo_deals:
        products = list(combo.products.all())
        total_products += len(products)

        current_total = sum([
            (
                product.sale_price
                if product.sale_price and product.sale_price < product.price
                else product.price
            ) or Decimal('0')
            for product in products
        ], Decimal('0'))

        original_total = sum([
            (product.price or Decimal('0'))
            for product in products
        ], Decimal('0'))

        if combo.discount_type == 'percentage':
            discount_amount = (
                    current_total * combo.discount_value / Decimal('100')
            ).quantize(money_round, rounding=ROUND_HALF_UP)
        else:
            discount_amount = Decimal(combo.discount_value or 0).quantize(
                money_round, rounding=ROUND_HALF_UP
            )

        if current_total > Decimal('0'):
            discount_amount = min(discount_amount, current_total)
            final_price = (
                    current_total - discount_amount
            ).quantize(money_round, rounding=ROUND_HALF_UP)
            discount_percent = int(
                min(
                    100,
                    (
                            discount_amount / current_total * 100
                    ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
                )
            )
        else:
            final_price = Decimal('0')
            discount_percent = 0

        if next_expiry is None or combo.valid_until < next_expiry:
            next_expiry = combo.valid_until

        total_discount_percent += Decimal(discount_percent)

        combo_cards.append({
            'combo': combo,
            'products': products,
            'original_total': original_total,
            'current_total': current_total,
            'discount_amount': discount_amount,
            'final_price': final_price,
            'discount_percent': discount_percent,
        })

    avg_discount_percent = round(
        float(total_discount_percent) / len(combo_cards), 1
    ) if combo_cards else 0

    context = {
        'combo_deals': combo_deals,
        'combo_cards': combo_cards,
        'combo_summary': {
            'active_count': len(combo_cards),
            'product_count': total_products,
            'next_expiry': next_expiry,
            'avg_discount_percent': avg_discount_percent,
        }
    }
    return render(request, 'promotions/combo_deal_list.html', context)


# =============================================================================
# VOUCHER VIEWS
# =============================================================================

@login_required
def my_vouchers(request):
    """
    Hiển thị danh sách Vouchers có thể sử dụng
    
    Yêu cầu đăng nhập để xem voucher cá nhân
    
    Chỉ hiển thị voucher:
    - Chưa hết hạn (valid_until >= now)
    - Đang active (is_active=True)
    
    Template: promotions/my_vouchers.html
    """
    now = timezone.now()

    # Lấy danh sách voucher còn hiệu lực
    vouchers = Voucher.objects.filter(
        valid_until__gte=now,  # Chưa hết hạn
        is_active=True  # Đang hoạt động
    ).order_by('-created_at')  # Mới nhất trước

    context = {
        'vouchers': vouchers,
    }
    return render(request, 'promotions/my_vouchers.html', context)


@login_required
def validate_voucher(request):
    """
    API: Xác thực mã voucher
    
    Kiểm tra mã voucher có hợp lệ không trước khi áp dụng
    
    Method: POST
    
    Request Body:
        - code: Mã voucher cần kiểm tra
        - cart_total: Tổng giá trị giỏ hàng
        
    Response:
        - valid: True/False
        - error: Thông báo lỗi (nếu không hợp lệ)
        - discount_type: Loại giảm giá (nếu hợp lệ)
        - discount_value: Giá trị giảm (nếu hợp lệ)
    """
    if request.method == 'POST':
        # Lấy dữ liệu từ request
        code = request.POST.get('code', '').strip()
        cart_total = float(request.POST.get('cart_total', 0))

        # Gọi service để xác thực
        result = PromotionService.validate_voucher(code, cart_total, request.user)
        return JsonResponse(result)

    # Chỉ chấp nhận POST request
    return JsonResponse({'valid': False, 'error': 'Yêu cầu không hợp lệ'})


@login_required
def apply_voucher(request):
    """
    API: Áp dụng voucher vào giỏ hàng
    
    Xác thực và tính toán số tiền giảm giá
    
    Method: POST
    
    Request Body:
        - code: Mã voucher cần áp dụng
        - cart_total: Tổng giá trị giỏ hàng
        
    Response (thành công):
        - success: True
        - voucher: Thông tin voucher (code, discount_type, discount_value)
        - discount_amount: Số tiền được giảm
        - final_total: Tổng tiền sau khi giảm
        
    Response (thất bại):
        - success: False
        - error: Thông báo lỗi
    """
    if request.method == 'POST':
        # Lấy dữ liệu từ request
        code = request.POST.get('code', '').strip()
        cart_total = float(request.POST.get('cart_total', 0))

        # Bước 1: Xác thực voucher
        validation = PromotionService.validate_voucher(code, cart_total, request.user)
        if not validation.get('valid'):
            return JsonResponse(validation)

        # Bước 2: Tính toán số tiền giảm
        voucher = Voucher.objects.get(code=code)
        discount = PromotionService.calculate_discount(voucher, cart_total)

        # Trả về kết quả
        return JsonResponse({
            'success': True,
            'voucher': {
                'code': voucher.code,
                'discount_type': voucher.discount_type,
                'discount_value': float(voucher.discount_value),
            },
            'discount_amount': discount,
            'final_total': cart_total - discount,
        })

    # Chỉ chấp nhận POST request
    return JsonResponse({'success': False, 'error': 'Yêu cầu không hợp lệ'})
