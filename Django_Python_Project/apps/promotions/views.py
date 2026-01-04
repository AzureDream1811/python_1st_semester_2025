"""
Views Khuyến Mãi cho ElectroShop
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
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
    """
    now = timezone.now()

    # Lấy danh sách flash sale đang diễn ra
    flash_sales = FlashSale.objects.filter(
        start_time__lte=now,  # Đã bắt đầu
        end_time__gte=now,  # Chưa kết thúc
        is_active=True  # Đang hoạt động
    ).select_related('product').order_by('end_time')  # Sắp hết trước

    context = {
        'flash_sales': flash_sales,
        'now': now,  # Để tính countdown trong template
    }
    return render(request, 'promotions/flash_sale_list.html', context)


def flash_sale_detail(request, pk):
    """
    Hiển thị chi tiết một Flash Sale
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
    """
    now = timezone.now()

    # Lấy danh sách combo đang có hiệu lực
    combo_deals = ComboDeal.objects.filter(
        valid_from__lte=now,  # Đã có hiệu lực
        valid_until__gte=now,  # Chưa hết hạn
        is_active=True  # Đang hoạt động
    ).prefetch_related('products').order_by('-created_at')  # Mới nhất trước

    context = {
        'combo_deals': combo_deals,
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
