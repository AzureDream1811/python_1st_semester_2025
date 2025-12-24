from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Voucher, ComboDeal, FlashSale
from .services.promotion_service import PromotionService


def flash_sale_list(request):
    """Danh sách Flash Sales đang diễn ra"""
    now = timezone.now()
    flash_sales = FlashSale.objects.filter(
        start_time__lte=now,
        end_time__gte=now,
        is_active=True
    ).select_related('product').order_by('end_time')
    
    context = {
        'flash_sales': flash_sales,
        'now': now,
    }
    return render(request, 'promotions/flash_sale_list.html', context)


def flash_sale_detail(request, pk):
    """Chi tiết Flash Sale"""
    flash_sale = get_object_or_404(FlashSale, pk=pk)
    
    context = {
        'flash_sale': flash_sale,
        'now': timezone.now(),
    }
    return render(request, 'promotions/flash_sale_detail.html', context)


def combo_deal_list(request):
    """Danh sách Combo Deals"""
    now = timezone.now()
    combo_deals = ComboDeal.objects.filter(
        valid_from__lte=now,
        valid_until__gte=now,
        is_active=True
    ).prefetch_related('products').order_by('-created_at')
    
    context = {
        'combo_deals': combo_deals,
    }
    return render(request, 'promotions/combo_deal_list.html', context)


@login_required
def my_vouchers(request):
    """Vouchers của user"""
    now = timezone.now()
    vouchers = Voucher.objects.filter(
        valid_until__gte=now,
        is_active=True
    ).order_by('-created_at')
    
    context = {
        'vouchers': vouchers,
    }
    return render(request, 'promotions/my_vouchers.html', context)


@login_required
def validate_voucher(request):
    """API: Validate voucher code"""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        cart_total = float(request.POST.get('cart_total', 0))
        
        result = PromotionService.validate_voucher(code, cart_total, request.user)
        return JsonResponse(result)
    
    return JsonResponse({'valid': False, 'error': 'Invalid request'})


@login_required
def apply_voucher(request):
    """API: Apply voucher to cart"""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        cart_total = float(request.POST.get('cart_total', 0))
        
        # Validate first
        validation = PromotionService.validate_voucher(code, cart_total, request.user)
        if not validation.get('valid'):
            return JsonResponse(validation)
        
        # Calculate discount
        voucher = Voucher.objects.get(code=code)
        discount = PromotionService.calculate_discount(voucher, cart_total)
        
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
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
